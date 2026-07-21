import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional

from ..schemas.student import LeaveApply, LeaveOut, AbsenteeOut, FineOut, StudentProfile
from ..services.leave_service import LeaveService
from ..repositories.student import StudentRepository
from ..repositories.absentee import AbsenteeRepository
from ..repositories.fine import FineRepository
from ..database.connection import get_db
from .deps import get_current_user, RoleChecker
from bson.objectid import ObjectId

router = APIRouter(prefix="/student", tags=["student"])
leave_service = LeaveService()
student_repo = StudentRepository()
absentee_repo = AbsenteeRepository()
fine_repo = FineRepository()

# Enforce student-only authorization on all student routes
student_auth = Depends(RoleChecker(["Student"]))

@router.post("/leave/apply", status_code=status.HTTP_201_CREATED)
async def apply_leave(
    current_user: dict = Depends(get_current_user),
    _=student_auth,
    leave_type: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    reason: str = Form(...),
    certificate: Optional[UploadFile] = File(None)
):
    """Submit a leave application with an optional certificate file upload."""
    try:
        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")

    certificate_url = None
    if certificate:
        import os, shutil, uuid
        upload_dir = os.path.join("uploads", "certificates")
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(certificate.filename)[1] if certificate.filename else ".pdf"
        fname = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(upload_dir, fname)
        with open(dest, "wb") as f:
            shutil.copyfileobj(certificate.file, f)
        certificate_url = f"/uploads/certificates/{fname}"

    leave_id = await leave_service.apply_for_leave(
        user_id=current_user["id"],
        start_date=start_dt,
        end_date=end_dt,
        leave_type=leave_type,
        reason=reason,
        certificate_url=certificate_url
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
    """Return authenticated student's profile."""
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    phone_num = student.get("phone") or student.get("mobile") or current_user.get("phone", "")

    return StudentProfile(
        registerNo=student.get("registerNo", ""),
        enrollNo=student.get("enrollNo", ""),
        fullName=student.get("fullName", ""),
        program=student.get("program", ""),
        departmentName=student.get("departmentName", student.get("department", "")),
        year=student.get("year", 1),
        semester=student.get("semester", 1),
        section=student.get("section", ""),
        attendancePercentage=student.get("attendancePercentage", 100.0),
        totalFine=student.get("totalFine", 0.0),
        phone=phone_num,
        mobile=phone_num,
        email=student.get("email", current_user.get("email", "")),
        address=student.get("address", current_user.get("address", ""))
    )


@router.put("/profile")
async def update_profile(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    _=student_auth
):
    """Update authenticated student's editable profile fields (phone, mobile, address, email)."""
    db = get_db()
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    update_fields = {}
    phone_val = payload.get("phone") or payload.get("mobile") or payload.get("phone_number")
    if phone_val:
        update_fields["phone"] = str(phone_val)
        update_fields["mobile"] = str(phone_val)

    if payload.get("address"):
        update_fields["address"] = str(payload["address"])

    if payload.get("email"):
        update_fields["email"] = str(payload["email"])

    if update_fields:
        update_fields["updatedAt"] = datetime.datetime.utcnow()
        # 1. Update in students collection
        await db.students.update_one(
            {"_id": student["_id"]},
            {"$set": update_fields}
        )
        # 2. Update in users collection
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_fields}
        )

    return {"message": "Profile updated successfully", "updatedFields": update_fields}


@router.get("/attendance")
async def get_attendance(current_user: dict = Depends(get_current_user), _=student_auth):
    """Alias: returns attendance records per subject for the student."""
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        return []
    db = get_db()
    # Fetch subject-wise attendance records from the attendance collection
    records = await db.attendance.find({"studentId": student["_id"]}).to_list(length=200)
    if not records:
        # Fall back: synthesise from absentee history for display purposes
        absences = await absentee_repo.get_by_student_id(str(student["_id"]))
        total_classes = max(60, len(absences) * 2 + 40)
        attended = total_classes - len(absences)
        pct = round((attended / total_classes) * 100, 1) if total_classes else 100.0
        return [{
            "subject": "Overall Attendance",
            "attendedClasses": attended,
            "totalClasses": total_classes,
            "percentage": pct
        }]
    result = []
    for r in records:
        r["_id"] = str(r["_id"])
        if r.get("studentId"): r["studentId"] = str(r["studentId"])
        result.append(r)
    return result


@router.get("/fines")
async def get_fines(current_user: dict = Depends(get_current_user), _=student_auth):
    """Alias for /fine/history — returns student fine records."""
    student = await student_repo.get_by_user_id(current_user["id"])
    if not student:
        return []
    fines = await fine_repo.get_by_student_id(str(student["_id"]))
    results = []
    for f in fines:
        results.append({
            "id": str(f["_id"]),
            "date": f["createdAt"].strftime("%Y-%m-%d") if f.get("createdAt") else None,
            "reason": f.get("reason", "Late fee"),
            "amount": f.get("amount", 0),
            "status": f.get("status", "Unpaid"),
            "receiptNo": f.get("receiptNo")
        })
    return results


@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user), _=student_auth):
    """Return in-app notifications for the authenticated student."""
    db = get_db()
    notifications = await db.notifications.find(
        {"recipientId": ObjectId(current_user["id"])}
    ).sort("createdAt", -1).limit(50).to_list(length=50)
    result = []
    for n in notifications:
        result.append({
            "id": str(n["_id"]),
            "title": n.get("title", "Notification"),
            "message": n.get("message", ""),
            "isRead": n.get("isRead", False),
            "createdAt": n["createdAt"].isoformat() if n.get("createdAt") else None
        })
    return result
