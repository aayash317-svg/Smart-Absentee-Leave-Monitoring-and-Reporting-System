"""
Dashboard route — provides role-aware metrics in a single endpoint.
Called by student, coordinator, hod, dean dashboard screens.
GET /api/dashboard/metrics → returns metrics appropriate for the calling user's role.
"""
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId

from .deps import get_current_user
from ..database.connection import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """
    Return role-appropriate dashboard metrics:
    - Student  → own attendance %, pending leaves, fine total
    - Coordinator/HOD → department stats, pending leave count
    - Dean     → institution-wide stats
    - Admin    → user counts, activity summary
    """
    db = get_db()
    role = current_user.get("role", "")

    if role == "Student":
        # Fetch student record supporting both string and ObjectId userId
        student = await db.students.find_one({
            "$or": [
                {"userId": str(current_user["id"])},
                {"userId": ObjectId(current_user["id"])}
            ]
        })
        if not student:
            # Fall back to profile data from user doc
            student = {
                "fullName": current_user.get("fullName", "Student"),
                "departmentName": current_user.get("department", "Engineering"),
                "year": 3,
                "semester": 6,
                "registerNo": current_user.get("register_number", current_user.get("id_number", "")),
                "attendancePercentage": float(current_user.get("attendance_percentage", 90.0) or 90.0),
                "totalFine": 0.0
            }

        student_id = student.get("_id")
        pending = 0
        if student_id:
            pending = await db.leaveApplications.count_documents({
                "studentId": student_id, "status": "Pending"
            })

        notifs = await db.notifications.find(
            {"recipientId": ObjectId(current_user["id"])}
        ).sort("createdAt", -1).limit(10).to_list(length=10)
        
        formatted_notifs = []
        for n in notifs:
            formatted_notifs.append({
                "title": n.get("title", "Notification"),
                "message": n.get("message", ""),
                "type": n.get("type", "Info"),
                "createdAt": n["createdAt"].isoformat() if n.get("createdAt") else ""
            })

        return {
            "role": "Student",
            "studentInfo": {
                "fullName": student.get("fullName", current_user.get("fullName", "")),
                "departmentName": student.get("departmentName", f"Department of {student.get('department', 'Engineering')}"),
                "year": student.get("year", 3),
                "semester": student.get("semester", 6),
                "registerNo": student.get("registerNo", current_user.get("register_number", ""))
            },
            "attendancePercentage": round(float(student.get("attendancePercentage", 90.0)), 1),
            "pendingLeavesCount": pending,
            "pendingLeaves": pending,
            "totalFine": round(float(student.get("totalFine", 0.0)), 2),
            "notifications": formatted_notifs
        }

    elif role in ("Coordinator", "HOD"):
        dept_id = current_user.get("departmentId")
        query = {}
        if dept_id:
            try:
                query["departmentId"] = ObjectId(dept_id) if isinstance(dept_id, str) else dept_id
            except Exception:
                pass
        total_students = await db.students.count_documents(query)
        pipeline = [{"$match": query}, {"$group": {"_id": None, "avg": {"$avg": "$attendancePercentage"}}}]
        result = []
        async for r in db.students.aggregate(pipeline):
            result.append(r)
        avg_att = result[0]["avg"] if result else 100.0
        low_att = await db.students.count_documents({**query, "attendancePercentage": {"$lt": 75.0}})
        student_ids = [s["_id"] async for s in db.students.find(query, {"_id": 1})]
        pending_leaves = await db.leaveApplications.count_documents({
            "studentId": {"$in": student_ids}, "status": "Pending"
        })
        return {
            "role": role,
            "totalStudents": total_students,
            "averageAttendance": round(avg_att, 1),
            "lowAttendanceCount": low_att,
            "pendingLeavesCount": pending_leaves,
        }

    elif role == "Dean":
        total_students = await db.students.count_documents({})
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$attendancePercentage"}}}]
        result = []
        async for r in db.students.aggregate(pipeline):
            result.append(r)
        avg_att = result[0]["avg"] if result else 100.0
        low_att = await db.students.count_documents({"attendancePercentage": {"$lt": 75.0}})
        pending = await db.leaveApplications.count_documents({"status": "Pending"})
        total_depts = await db.departments.count_documents({})
        return {
            "role": "Dean",
            "totalStudents": total_students,
            "averageAttendance": round(avg_att, 1),
            "lowAttendanceCount": low_att,
            "pendingLeavesCount": pending,
            "totalDepartments": total_depts,
        }

    elif role in ("Admin", "Faculty"):
        total_users = await db.users.count_documents({"isDeleted": {"$ne": True}})
        total_students = await db.students.count_documents({})
        recent_logs = await db.audit_logs.count_documents({
            "createdAt": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(days=1)}
        })
        return {
            "role": role,
            "totalUsers": total_users,
            "totalStudents": total_students,
            "recentActivityCount": recent_logs,
        }

    return {"role": role, "message": "No metrics available for this role"}
