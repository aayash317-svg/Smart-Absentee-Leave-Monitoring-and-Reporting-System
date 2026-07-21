import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from ..schemas.coordinator import MarkAbsent, LeaveAction
from ..services.leave_service import LeaveService
from ..repositories.student import StudentRepository
from ..repositories.absentee import AbsenteeRepository
from .deps import get_current_user, RoleChecker

router = APIRouter(prefix="/coordinator", tags=["coordinator"])
leave_service = LeaveService()
student_repo = StudentRepository()
absentee_repo = AbsenteeRepository()

# Enforce coordinator/HOD/Dean auth
coordinator_auth = Depends(RoleChecker(["Coordinator", "HOD", "Dean", "Admin"]))

@router.post("/attendance/mark")
async def mark_student_absent(req: MarkAbsent, current_user: dict = Depends(get_current_user), _=coordinator_auth):
    try:
        absent_dt = datetime.datetime.strptime(req.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
        
    # Check if student exists
    student = await student_repo.get_by_id(req.studentId)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check department scope
    if current_user.get("role") == "Coordinator":
        if not student.get("departmentId") or str(student["departmentId"]) != str(current_user.get("departmentId")):
            raise HTTPException(status_code=403, detail="You can only manage students in your own department")

    # Check if duplicate entry
    is_duplicate = await absentee_repo.check_existence(req.studentId, absent_dt)
    if is_duplicate:
        raise HTTPException(status_code=400, detail="Student is already marked absent for this date")

    # Insert absentee record
    absentee_id = await absentee_repo.create({
        "studentId": student["_id"],
        "date": absent_dt,
        "reason": req.reason,
        "status": req.status,
        "markedBy": ObjectId(current_user["id"]),
        "leaveApplicationId": None,
        "createdAt": datetime.datetime.utcnow()
    })
    
    # Recompute student's attendance percentage
    current_att = student.get("attendancePercentage", 90.0)
    new_att = max(0.0, current_att - 2.5)
    new_att = round(new_att, 1)
    await student_repo.update(str(student["_id"]), {"attendancePercentage": new_att})
    
    db = absentee_repo.collection.database
    # Update in users collection
    await db.users.update_one({"_id": ObjectId(student["userId"])}, {"$set": {"attendance_percentage": str(new_att)}})
    
    # Trigger low attendance alert thresholds
    from ..utils.attendance import process_attendance_notifications
    await process_attendance_notifications(db, student, current_att, new_att)
    
    return {"message": "Student marked absent successfully", "absenteeId": absentee_id, "newAttendancePercentage": new_att}

@router.put("/leave/action/{leave_id}")
async def process_leave(leave_id: str, req: LeaveAction, current_user: dict = Depends(get_current_user), _=coordinator_auth):
    # Fetch leave application
    leave = await leave_service.leave_repo.get_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave application not found")
        
    student = await student_repo.get_by_id(str(leave["studentId"]))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check department scope
    if current_user.get("role") == "Coordinator":
        if not student.get("departmentId") or str(student["departmentId"]) != str(current_user.get("departmentId")):
            raise HTTPException(status_code=403, detail="You can only manage leaves for students in your own department")

    if req.action == "approve":
        return await leave_service.approve_leave(
            leave_app_id=leave_id,
            coordinator_user_id=current_user["id"]
        )
    elif req.action == "reject":
        reason = req.reason or "Rejected by coordinator"
        return await leave_service.reject_leave(
            leave_app_id=leave_id,
            coordinator_user_id=current_user["id"],
            reason=reason
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid action, must be 'approve' or 'reject'")

@router.get("/students/search")
async def search_students(query: Optional[str] = None, current_user: dict = Depends(get_current_user), _=coordinator_auth):
    # Retrieve students belonging to coordinator's department if they are a coordinator
    dept_id = str(current_user["departmentId"]) if current_user.get("departmentId") else None
    students = await student_repo.search_students(query=query, department_id=dept_id)
    
    results = []
    for s in students:
        s["id"] = str(s["_id"])
        s["userId"] = str(s["userId"])
        s["departmentId"] = str(s["departmentId"])
        s.pop("_id")
        results.append(s)
    return results

@router.get("/leave/pending")
async def get_pending_leaves(current_user: dict = Depends(get_current_user), _=coordinator_auth):
    dept_id = current_user.get("departmentId")
    if dept_id:
        # Fetch department students
        dept_students = await student_repo.find_all({"departmentId": dept_id})
        student_ids = [str(s["_id"]) for s in dept_students]
        leaves = await leave_service.leave_repo.get_pending_leaves_by_students(student_ids)
    else:
        leaves = await leave_service.leave_repo.get_pending_leaves()
        
    results = []
    for l in leaves:
        # Fetch student details
        student_rec = await student_repo.get_by_id(str(l["studentId"]))
        student_name = student_rec["fullName"] if student_rec else "Unknown Student"
        reg_no = student_rec["registerNo"] if student_rec else "N/A"
        
        results.append({
            "id": str(l["_id"]),
            "studentId": str(l["studentId"]),
            "studentName": student_name,
            "registerNo": reg_no,
            "startDate": l["startDate"].strftime("%Y-%m-%d"),
            "endDate": l["endDate"].strftime("%Y-%m-%d"),
            "leaveType": l["leaveType"],
            "reason": l["reason"],
            "status": l["status"],
            "appliedDate": l["appliedDate"].strftime("%Y-%m-%d %H:%M:%S")
        })
    return results

# ── Alias routes used by frontend screens ─────────────────────────────────

@router.get("/students")
async def list_students(current_user: dict = Depends(get_current_user), _=coordinator_auth):
    """List students in coordinator's department (frontend faculty marking screen)."""
    dept_id = current_user.get("departmentId")
    students = await student_repo.search_students(query=None, department_id=str(dept_id) if dept_id else None)
    result = []
    for s in students:
        result.append({
            "_id": str(s["_id"]),
            "registerNo": s.get("registerNo", ""),
            "fullName": s.get("fullName", ""),
            "year": s.get("year", 1),
            "section": s.get("section", ""),
        })
    return result

class BulkAbsentRequest(BaseModel):
    student_ids: List[str]
    date: str
    reason: str = "Absent"

@router.post("/mark-absent")
async def mark_bulk_absent(req: BulkAbsentRequest, current_user: dict = Depends(get_current_user), _=coordinator_auth):
    """Mark a list of student IDs as absent for a given date (bulk operation)."""
    try:
        absent_dt = datetime.datetime.strptime(req.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    marked = []
    skipped = []
    db = absentee_repo.collection.database
    
    for sid in req.student_ids:
        student = await student_repo.get_by_id(sid)
        if not student:
            skipped.append(sid)
            continue
            
        # Check department scope
        if current_user.get("role") == "Coordinator":
            if not student.get("departmentId") or str(student["departmentId"]) != str(current_user.get("departmentId")):
                skipped.append(sid)
                continue

        is_dup = await absentee_repo.check_existence(sid, absent_dt)
        if is_dup:
            skipped.append(sid)
            continue
            
        await absentee_repo.create({
            "studentId": student["_id"],
            "date": absent_dt,
            "reason": req.reason,
            "status": "Absent",
            "markedBy": ObjectId(current_user["id"]),
            "leaveApplicationId": None,
            "createdAt": datetime.datetime.utcnow()
        })
        
        current_att = student.get("attendancePercentage", 90.0)
        new_att = max(0.0, current_att - 2.5)
        new_att = round(new_att, 1)
        await student_repo.update(str(student["_id"]), {"attendancePercentage": new_att})
        
        # Update user doc
        await db.users.update_one({"_id": ObjectId(student["userId"])}, {"$set": {"attendance_percentage": str(new_att)}})
        
        # Trigger warnings
        from ..utils.attendance import process_attendance_notifications
        await process_attendance_notifications(db, student, current_att, new_att)
        marked.append(sid)

    return {"message": f"Marked {len(marked)} student(s) absent", "marked": marked, "skipped": skipped}
