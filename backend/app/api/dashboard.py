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
        # Fetch student record
        student = await db.students.find_one({"userId": ObjectId(current_user["id"])})
        if not student:
            return {"role": "Student", "attendancePercentage": 100.0, "pendingLeaves": 0, "totalFine": 0.0}
        pending = await db.leaveApplications.count_documents({
            "studentId": student["_id"], "status": "Pending"
        })
        return {
            "role": "Student",
            "fullName": student.get("fullName", ""),
            "attendancePercentage": round(student.get("attendancePercentage", 100.0), 1),
            "pendingLeaves": pending,
            "totalFine": round(student.get("totalFine", 0.0), 2),
            "registerNo": student.get("registerNo", ""),
            "year": student.get("year", 1),
            "semester": student.get("semester", 1),
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
