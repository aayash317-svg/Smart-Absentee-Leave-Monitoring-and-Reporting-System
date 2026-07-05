import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import Optional

from ..db import get_db
from .auth import get_current_user_from_token, safe_object_id

router = APIRouter(prefix="/api/leave", tags=["leave"])

class LeaveApplyRequest(BaseModel):
    startDate: str  # YYYY-MM-DD
    endDate: str    # YYYY-MM-DD
    leaveType: str  # Sick Leave, Duty Leave, Casual Leave, Other
    reason: str

@router.post("/apply")
def apply_leave(req: LeaveApplyRequest, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    # Verify user is student
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] != "Student":
        raise HTTPException(status_code=403, detail="Only students can apply for leave")
        
    student = db.students.find_one({"userId": safe_object_id(user_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    try:
        start_dt = datetime.datetime.strptime(req.startDate, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(req.endDate, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
        
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")

    # --- BUG FIX: Prevent duplicate overlapping leave applications ---
    overlapping = db.leaveApplications.find_one({
        "studentId": student["_id"],
        "status": {"$in": ["Pending", "Approved"]},
        "startDate": {"$lte": end_dt},
        "endDate": {"$gte": start_dt}
    })
    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="A leave application already exists for overlapping dates"
        )
        
    leave_doc = {
        "studentId": student["_id"],
        "startDate": start_dt,
        "endDate": end_dt,
        "leaveType": req.leaveType,
        "reason": req.reason,
        "status": "Pending",
        "approvedBy": None,
        "appliedDate": datetime.datetime.utcnow(),
        "updatedAt": datetime.datetime.utcnow()
    }
    
    result = db.leaveApplications.insert_one(leave_doc)
    
    # Audit log
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Applied Leave",
        "details": f"Applied for {req.leaveType} from {req.startDate} to {req.endDate}",
        "createdAt": datetime.datetime.utcnow()
    })
    
    return {"message": "Leave application submitted successfully", "applicationId": str(result.inserted_id)}

@router.get("/history")
def get_leave_history(user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user["role"] == "Student":
        student = db.students.find_one({"userId": safe_object_id(user_id)})
        if not student:
            return []
        query = {"studentId": student["_id"]}
    else:
        # Staff query
        dept_id = user.get("departmentId")
        if not dept_id:
            raise HTTPException(status_code=400, detail="Staff has no department assigned")
        dept_students = [s["_id"] for s in db.students.find({"departmentId": dept_id}, {"_id": 1})]
        query = {"studentId": {"$in": dept_students}}
        
    leaves = list(db.leaveApplications.find(query).sort("appliedDate", -1))
    for l in leaves:
        l["_id"] = str(l["_id"])
        # Fetch student info for staff display
        student_rec = db.students.find_one({"_id": l["studentId"]}, {"fullName": 1, "registerNo": 1})
        if student_rec:
            l["studentName"] = student_rec["fullName"]
            l["registerNo"] = student_rec["registerNo"]
        l["studentId"] = str(l["studentId"])
        l["startDate"] = l["startDate"].strftime("%Y-%m-%d")
        l["endDate"] = l["endDate"].strftime("%Y-%m-%d")
        l["appliedDate"] = l["appliedDate"].strftime("%Y-%m-%d")
        if l.get("approvedBy"):
            l["approvedBy"] = str(l["approvedBy"])
            
    return leaves

@router.put("/approve/{app_id}")
def approve_leave(app_id: str, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    # Verify user is Staff (Dean, HOD, Coordinator)
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] not in ["Dean", "HOD", "Coordinator"]:
        raise HTTPException(status_code=403, detail="Unauthorized to approve leave applications")
        
    leave_app = db.leaveApplications.find_one({"_id": safe_object_id(app_id)})
    if not leave_app:
        raise HTTPException(status_code=404, detail="Leave application not found")
        
    # Update leave status
    db.leaveApplications.update_one(
        {"_id": safe_object_id(app_id)},
        {"$set": {
            "status": "Approved",
            "approvedBy": safe_object_id(user_id),
            "updatedAt": datetime.datetime.utcnow()
        }}
    )
    
    # Notify student
    student = db.students.find_one({"_id": leave_app["studentId"]})
    if student:
        # Change unexcused absentees in the date range to excused
        db.absentees.update_many(
            {
                "studentId": student["_id"],
                "date": {
                    "$gte": leave_app["startDate"],
                    "$lte": leave_app["endDate"]
                }
            },
            {"$set": {"status": "Excused"}}
        )
        
        # Calculate new attendance percentage based on updated absentees if we had full logging, 
        # let's increment attendance slightly for prototype purposes
        new_percentage = min(student.get("attendancePercentage", 70.0) + 2.0, 100.0)
        db.students.update_one(
            {"_id": student["_id"]},
            {"$set": {"attendancePercentage": round(new_percentage, 1)}}
        )
        
        # Send Notification
        db.notifications.insert_one({
            "recipientId": student["userId"],
            "title": "Leave Approved",
            "message": f"Your leave request for {leave_app['leaveType']} from {leave_app['startDate'].strftime('%Y-%m-%d')} to {leave_app['endDate'].strftime('%Y-%m-%d')} has been approved.",
            "type": "Leave Status",
            "isRead": False,
            "createdAt": datetime.datetime.utcnow()
        })
        
    # Log Audit
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Approved Leave",
        "details": f"Approved leave ID {app_id} for student ID {str(leave_app['studentId'])}",
        "createdAt": datetime.datetime.utcnow()
    })
    
    return {"message": "Leave application approved successfully"}

@router.put("/reject/{app_id}")
def reject_leave(app_id: str, reason: Optional[str] = "Rejected by authority", user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    # Verify user is Staff
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] not in ["Dean", "HOD", "Coordinator"]:
        raise HTTPException(status_code=403, detail="Unauthorized to reject leave applications")
        
    leave_app = db.leaveApplications.find_one({"_id": safe_object_id(app_id)})
    if not leave_app:
        raise HTTPException(status_code=404, detail="Leave application not found")
        
    # Update leave status
    db.leaveApplications.update_one(
        {"_id": safe_object_id(app_id)},
        {"$set": {
            "status": "Rejected",
            "approvedBy": safe_object_id(user_id),
            "updatedAt": datetime.datetime.utcnow()
        }}
    )
    
    # Notify student
    student = db.students.find_one({"_id": leave_app["studentId"]})
    if student:
        db.notifications.insert_one({
            "recipientId": student["userId"],
            "title": "Leave Rejected",
            "message": f"Your leave request for {leave_app['leaveType']} from {leave_app['startDate'].strftime('%Y-%m-%d')} to {leave_app['endDate'].strftime('%Y-%m-%d')} has been rejected. Reason: {reason}",
            "type": "Leave Status",
            "isRead": False,
            "createdAt": datetime.datetime.utcnow()
        })
        
    # Log Audit
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Rejected Leave",
        "details": f"Rejected leave ID {app_id} for student ID {str(leave_app['studentId'])}. Reason: {reason}",
        "createdAt": datetime.datetime.utcnow()
    })
    
    return {"message": "Leave application rejected successfully"}

