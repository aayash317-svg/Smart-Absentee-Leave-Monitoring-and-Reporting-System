import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..schemas.student import LeaveApply, LeaveOut, AbsenteeOut, FineOut, StudentProfile
from ..services.leave_service import LeaveService
from ..repositories.student import StudentRepository
from ..repositories.absentee import AbsenteeRepository
from ..repositories.fine import FineRepository
from .deps import get_current_user, RoleChecker

router = APIRouter(prefix="/student", tags=["student"])
leave_service = LeaveService()
student_repo = StudentRepository()
absentee_repo = AbsenteeRepository()
fine_repo = FineRepository()

# Enforce student-only authorization on all student routes
student_auth = Depends(RoleChecker(["Student"]))

@router.post("/leave/apply", status_code=status.HTTP_201_CREATED)
async def apply_leave(req: LeaveApply, current_user: dict = Depends(get_current_user), _=student_auth):
    try:
        start_dt = datetime.datetime.strptime(req.startDate, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(req.endDate, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
        
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")
        
    leave_id = await leave_service.apply_for_leave(
        user_id=current_user["id"],
        start_date=start_dt,
        end_date=end_dt,
        leave_type=req.leaveType,
        reason=req.reason,
        certificate_url=req.certificateUrl
    )
    
    return {"message": "Leave application submitted successfully", "applicationId": leave_id}

@router.get("/leave/history", response_model=List[LeaveOut])
async def get_leave_history(current_user: dict = Depends(get_current_user), _=student_auth):
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        return []
        
    leaves = await leave_service.leave_repo.get_by_student_id(str(student["_id"]))
    
    results = []
    for l in leaves:
        results.append(LeaveOut(
            id=str(l["_id"]),
            startDate=l["startDate"].strftime("%Y-%m-%d"),
            endDate=l["endDate"].strftime("%Y-%m-%d"),
            leaveType=l["leaveType"],
            reason=l["reason"],
            certificateUrl=l.get("certificateUrl"),
            status=l["status"],
            appliedDate=l["appliedDate"].strftime("%Y-%m-%d %H:%M:%S")
        ))
    return results

@router.get("/absentee/history", response_model=List[AbsenteeOut])
async def get_absentee_history(current_user: dict = Depends(get_current_user), _=student_auth):
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        return []
        
    absences = await absentee_repo.get_by_student_id(str(student["_id"]))
    
    results = []
    for a in absences:
        results.append(AbsenteeOut(
            id=str(a["_id"]),
            date=a["date"].strftime("%Y-%m-%d"),
            reason=a.get("reason", "Absent"),
            status=a["status"]
        ))
    return results

@router.get("/fine/history", response_model=List[FineOut])
async def get_fine_history(current_user: dict = Depends(get_current_user), _=student_auth):
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        return []
        
    fines = await fine_repo.get_by_student_id(str(student["_id"]))
    
    results = []
    for f in fines:
        results.append(FineOut(
            id=str(f["_id"]),
            amount=f["amount"],
            status=f["status"],
            receiptNo=f.get("receiptNo"),
            createdAt=f["createdAt"].strftime("%Y-%m-%d %H:%M:%S"),
            paymentDate=f["paymentDate"].strftime("%Y-%m-%d %H:%M:%S") if f.get("paymentDate") else None
        ))
    return results

@router.get("/profile", response_model=StudentProfile)
async def get_profile(current_user: dict = Depends(get_current_user), _=student_auth):
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    return StudentProfile(
        registerNo=student["registerNo"],
        enrollNo=student["enrollNo"],
        fullName=student["fullName"],
        program=student["program"],
        departmentName=student["departmentName"],
        year=student["year"],
        semester=student["semester"],
        section=student["section"],
        attendancePercentage=student["attendancePercentage"],
        totalFine=student["totalFine"]
    )
