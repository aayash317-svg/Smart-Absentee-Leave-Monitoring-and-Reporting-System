import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import Optional

from ..db import get_db
from .auth import get_current_user_from_token, safe_object_id

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

class MarkAbsentRequest(BaseModel):
    studentId: str
    date: str  # YYYY-MM-DD
    reason: Optional[str] = "Absent"
    status: str = "Unexcused" # Unexcused, Excused

@router.post("/mark")
def mark_attendance(req: MarkAbsentRequest, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()

    # Verify user is Staff / Faculty
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] not in ["Dean", "HOD", "Coordinator", "Faculty"]:
        raise HTTPException(status_code=403, detail="Unauthorized to mark attendance")

    student = db.students.find_one({"_id": safe_object_id(req.studentId)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # --- BUG FIX: Department scope restriction for Faculty ---
    # Faculty can only mark students in their own department.
    # Dean / HOD / Coordinator have broader access.
    if user["role"] == "Faculty":
        faculty_dept = user.get("departmentId")
        student_dept = student.get("departmentId")
        if faculty_dept and student_dept and str(faculty_dept) != str(student_dept):
            raise HTTPException(
                status_code=403,
                detail="Faculty can only mark attendance for students in their own department"
            )

    try:
        absent_date = datetime.datetime.strptime(req.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    # --- BUG FIX: Prevent marking future dates as absent ---
    if absent_date.date() > datetime.datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="Cannot mark attendance for a future date")

    # Check if already marked absent for this date
    existing = db.absentees.find_one({
        "studentId": safe_object_id(req.studentId),
        "date": absent_date
    })
    if existing:
        raise HTTPException(status_code=400, detail="Student already marked absent for this date")

    # Insert absentee record
    db.absentees.insert_one({
        "studentId": safe_object_id(req.studentId),
        "date": absent_date,
        "reason": req.reason,
        "status": req.status,
        "markedBy": safe_object_id(user_id),
        "createdAt": datetime.datetime.utcnow()
    })

    # --- BUG FIX: Real attendance formula ---
    # Use totalClasses and classesAttended fields on student document.
    # If these fields don't exist yet, bootstrap from current attendancePercentage.
    total_classes = student.get("totalClasses", 100)
    classes_attended = student.get("classesAttended",
        int(round(student.get("attendancePercentage", 75.0) / 100 * total_classes))
    )

    # One more class was held today that the student missed
    new_total = total_classes + 1
    # classesAttended stays the same (student was absent)
    new_attended = classes_attended
    new_att = round((new_attended / new_total) * 100, 1) if new_total > 0 else 0.0

    db.students.update_one(
        {"_id": safe_object_id(req.studentId)},
        {"$set": {
            "attendancePercentage": new_att,
            "totalClasses": new_total,
            "classesAttended": new_attended
        }}
    )

    # Check if attendance drops below 75% -> trigger warning notification
    current_att = student.get("attendancePercentage", 75.0)
    if new_att < 75.0 and current_att >= 75.0:
        db.notifications.insert_one({
            "recipientId": student["userId"],
            "title": "Low Attendance Alert",
            "message": f"Your attendance has dropped to {new_att}%, which is below the threshold of 75%. Please contact your coordinator.",
            "type": "Warning",
            "isRead": False,
            "createdAt": datetime.datetime.utcnow()
        })

    # Audit log
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Marked Absent",
        "details": f"Marked student {student['fullName']} absent on {req.date}. New attendance: {new_att}%",
        "createdAt": datetime.datetime.utcnow()
    })

    return {"message": "Attendance marked successfully", "newAttendancePercentage": new_att}

@router.get("/notifications")
def get_notifications(user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    notifs = list(db.notifications.find({"recipientId": safe_object_id(user_id)}).sort("createdAt", -1))
    for n in notifs:
        n["_id"] = str(n["_id"])
        n["recipientId"] = str(n["recipientId"])
        n["createdAt"] = n["createdAt"].isoformat()
    return notifs

@router.put("/notifications/read/{notif_id}")
def mark_notification_read(notif_id: str, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    db.notifications.update_one(
        {"_id": safe_object_id(notif_id), "recipientId": safe_object_id(user_id)},
        {"$set": {"isRead": True}}
    )
    return {"message": "Notification marked as read"}

