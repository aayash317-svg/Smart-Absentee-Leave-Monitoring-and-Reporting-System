import datetime
from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from fastapi import HTTPException, status

from ..repositories.leave import LeaveRepository
from ..repositories.student import StudentRepository
from ..repositories.absentee import AbsenteeRepository
from ..repositories.user import UserRepository
from .fine_service import FineService

class LeaveService:
    def __init__(self):
        self.leave_repo = LeaveRepository()
        self.student_repo = StudentRepository()
        self.absentee_repo = AbsenteeRepository()
        self.user_repo = UserRepository()
        self.fine_service = FineService()

    async def apply_for_leave(
        self, 
        user_id: str, 
        start_date: datetime.datetime, 
        end_date: datetime.datetime, 
        leave_type: str, 
        reason: str, 
        certificate_url: Optional[str] = None
    ) -> str:
        # Get student profile
        student = await self.student_repo.get_by_user_id(user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student record not found")
            
        leave_doc = {
            "studentId": student["_id"],
            "startDate": start_date,
            "endDate": end_date,
            "leaveType": leave_type,
            "reason": reason,
            "certificateUrl": certificate_url,
            "status": "Pending",
            "approvedBy": None,
            "appliedDate": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        }
        
        # Save leave
        leave_id = await self.leave_repo.create(leave_doc)
        
        # Log Audit event (stubbed)
        db = self.leave_repo.collection.database
        await db.audit_logs.insert_one({
            "userId": ObjectId(user_id),
            "action": "Applied Leave",
            "details": f"Applied for {leave_type} from {start_date.date()} to {end_date.date()}",
            "createdAt": datetime.datetime.utcnow()
        })
        
        return leave_id

    async def approve_leave(self, leave_app_id: str, coordinator_user_id: str) -> Dict[str, Any]:
        # Fetch leave application
        leave = await self.leave_repo.get_by_id(leave_app_id)
        if not leave:
            raise HTTPException(status_code=404, detail="Leave application not found")
            
        if leave["status"] != "Pending":
            raise HTTPException(status_code=400, detail="Leave application has already been processed")

        # 1. Calculate delayed submission fine
        # Compares absence date (startDate) and appliedDate
        fine_amount = await self.fine_service.calculate_delay_fine(
            absent_date=leave["startDate"],
            applied_date=leave["appliedDate"]
        )
        
        # 2. Update Leave application status
        await self.leave_repo.update(leave_app_id, {
            "status": "Approved",
            "approvedBy": ObjectId(coordinator_user_id),
            "updatedAt": datetime.datetime.utcnow()
        })
        
        # 3. Excused absentees in the date range
        db = self.leave_repo.collection.database
        await db.absentees.update_many(
            {
                "studentId": leave["studentId"],
                "date": {
                    "$gte": leave["startDate"],
                    "$lte": leave["endDate"]
                }
            },
            {"$set": {"status": "Excused", "leaveApplicationId": ObjectId(leave_app_id)}}
        )
        
        # 4. If fine exists, create transaction
        tx_id = None
        if fine_amount > 0:
            tx_id = await self.fine_service.generate_fine_transaction(
                student_id=str(leave["studentId"]),
                leave_app_id=leave_app_id,
                amount=fine_amount
            )
            # Add to student's total outstanding fine
            await self.student_repo.collection.update_one(
                {"_id": leave["studentId"]},
                {"$inc": {"totalFine": fine_amount}}
            )

        # 5. Fetch student details to get their user ID for notification dispatch
        student = await self.student_repo.get_by_id(str(leave["studentId"]))
        if student:
            # Create a notification in the database
            await db.notifications.insert_one({
                "recipientId": student["userId"],
                "title": "Leave Application Approved",
                "message": f"Your leave request has been approved. Delayed submission fine: ₹{fine_amount}",
                "type": "Student",
                "isRead": False,
                "createdAt": datetime.datetime.utcnow()
            })
            
            # Recompute student's attendance percentage (simulated)
            current_att = student.get("attendancePercentage", 80.0)
            new_att = min(current_att + 2.0, 100.0)
            await self.student_repo.update(str(student["_id"]), {"attendancePercentage": round(new_att, 1)})
            
        return {"message": "Leave application approved", "fineAmountApplied": fine_amount, "transactionId": tx_id}

    async def reject_leave(self, leave_app_id: str, coordinator_user_id: str, reason: str) -> Dict[str, Any]:
        leave = await self.leave_repo.get_by_id(leave_app_id)
        if not leave:
            raise HTTPException(status_code=404, detail="Leave application not found")
            
        if leave["status"] != "Pending":
            raise HTTPException(status_code=400, detail="Leave application has already been processed")
            
        await self.leave_repo.update(leave_app_id, {
            "status": "Rejected",
            "approvedBy": ObjectId(coordinator_user_id),
            "updatedAt": datetime.datetime.utcnow()
        })
        
        student = await self.student_repo.get_by_id(str(leave["studentId"]))
        if student:
            db = self.leave_repo.collection.database
            await db.notifications.insert_one({
                "recipientId": student["userId"],
                "title": "Leave Application Rejected",
                "message": f"Your leave request was rejected. Reason: {reason}",
                "type": "Student",
                "isRead": False,
                "createdAt": datetime.datetime.utcnow()
            })
            
        return {"message": "Leave application rejected"}
