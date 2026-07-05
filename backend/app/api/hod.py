from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId
import datetime

from ..database.connection import get_db
from ..api.deps import get_current_user
from ..core.permissions import require_hod
from ..services.report_service import ReportService
from ..services.leave_service import LeaveService

router = APIRouter(prefix="/hod", tags=["hod"])
leave_service = LeaveService()

class RejectLeaveRequest(BaseModel):
    reason: str

@router.get("/metrics")
async def get_department_metrics(current_user: dict = Depends(get_current_user), _=Depends(require_hod)):
    """Fetch aggregated metrics for the HOD's department."""
    db = get_db()
    dept_id = current_user.get("departmentId")
    if not dept_id:
        raise HTTPException(status_code=400, detail="HOD is not assigned to a department")
        
    dept_obj_id = ObjectId(dept_id) if isinstance(dept_id, str) else dept_id
    
    total_students = await db.students.count_documents({"departmentId": dept_obj_id})
    
    pipeline = [
        {"$match": {"departmentId": dept_obj_id}},
        {"$group": {"_id": None, "avg_att": {"$avg": "$attendancePercentage"}}}
    ]
    result = []
    cursor = db.students.aggregate(pipeline)
    async for r in cursor:
        result.append(r)
    avg_attendance = result[0]["avg_att"] if result else 100.0
    
    low_att_count = await db.students.count_documents({
        "departmentId": dept_obj_id,
        "attendancePercentage": {"$lt": 75.0}
    })
    
    # Get pending leaves count
    student_ids = [s["_id"] for s in await db.students.find({"departmentId": dept_obj_id}, {"_id": 1}).to_list(length=1000)]
    pending_leaves = await db.leaveApplications.count_documents({
        "studentId": {"$in": student_ids},
        "status": "Pending"
    })
    
    return {
        "role": "HOD",
        "departmentId": str(dept_id),
        "totalStudents": total_students,
        "averageAttendance": round(avg_attendance, 2),
        "lowAttendanceCount": low_att_count,
        "pendingLeavesCount": pending_leaves
    }

@router.get("/report/excel")
async def download_department_report(current_user: dict = Depends(get_current_user), _=Depends(require_hod)):
    """Generate and download the attendance report spreadsheet for the HOD's department."""
    dept_id = current_user.get("departmentId")
    if not dept_id:
        raise HTTPException(status_code=400, detail="HOD is not assigned to a department")
        
    excel_bytes = await ReportService.get_department_excel(str(dept_id))
    if not excel_bytes:
        raise HTTPException(status_code=404, detail="No student records found in department")
        
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=department_attendance_{str(dept_id)}.xlsx"}
    )

@router.get("/leaves/pending")
async def get_pending_leaves(current_user: dict = Depends(get_current_user), _=Depends(require_hod)):
    """List pending leave applications submitted by students in the HOD's department."""
    db = get_db()
    dept_id = current_user.get("departmentId")
    if not dept_id:
        raise HTTPException(status_code=400, detail="HOD is not assigned to a department")
        
    dept_obj_id = ObjectId(dept_id) if isinstance(dept_id, str) else dept_id
    
    students = await db.students.find({"departmentId": dept_obj_id}).to_list(length=1000)
    student_map = {s["_id"]: s for s in students}
    student_ids = list(student_map.keys())
    
    leaves = await db.leaveApplications.find({
        "studentId": {"$in": student_ids},
        "status": "Pending"
    }).sort("appliedDate", -1).to_list(length=100)
    
    results = []
    for l in leaves:
        student_rec = student_map.get(l["studentId"])
        results.append({
            "id": str(l["_id"]),
            "studentId": str(l["studentId"]),
            "studentName": student_rec["fullName"] if student_rec else "Unknown",
            "registerNo": student_rec["registerNo"] if student_rec else "N/A",
            "startDate": l["startDate"].strftime("%Y-%m-%d"),
            "endDate": l["endDate"].strftime("%Y-%m-%d"),
            "leaveType": l["leaveType"],
            "reason": l["reason"],
            "certificateUrl": l.get("certificateUrl"),
            "status": l["status"],
            "appliedDate": l["appliedDate"].strftime("%Y-%m-%d %H:%M")
        })
    return results

@router.post("/leaves/approve/{leave_id}")
async def approve_leave(leave_id: str, current_user: dict = Depends(get_current_user), _=Depends(require_hod)):
    """Approve a leave application."""
    res = await leave_service.approve_leave(leave_app_id=leave_id, coordinator_user_id=current_user["id"])
    return res

@router.post("/leaves/reject/{leave_id}")
async def reject_leave(leave_id: str, req: RejectLeaveRequest, current_user: dict = Depends(get_current_user), _=Depends(require_hod)):
    """Reject a leave application with a specified reason."""
    res = await leave_service.reject_leave(leave_app_id=leave_id, coordinator_user_id=current_user["id"], reason=req.reason)
    return res
