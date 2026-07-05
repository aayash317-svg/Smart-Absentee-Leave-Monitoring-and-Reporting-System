from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId
from typing import Optional

from ..db import get_db
from .auth import get_current_user_from_token, safe_object_id

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics")
def get_dashboard_metrics(user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    # Fetch user first
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    role = user["role"]
    dept_id = user.get("departmentId")
    
    # 1. Student Dashboard Metrics
    if role == "Student":
        student = db.students.find_one({"userId": safe_object_id(user_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student record not found")
            
        student_id = student["_id"]
        
        # Count pending leaves
        pending_leaves = db.leaveApplications.count_documents({
            "studentId": student_id,
            "status": "Pending"
        })
        
        # Count unexcused absentees
        unexcused_count = db.absentees.count_documents({
            "studentId": student_id,
            "status": "Unexcused"
        })
        
        # Fetch notifications
        notifications = list(db.notifications.find({"recipientId": safe_object_id(user_id)}).sort("createdAt", -1).limit(5))
        for n in notifications:
            n["_id"] = str(n["_id"])
            n["recipientId"] = str(n["recipientId"])
            if "createdAt" in n:
                n["createdAt"] = n["createdAt"].isoformat()
                
        # Fetch leave history
        leaves = list(db.leaveApplications.find({"studentId": student_id}).sort("startDate", -1).limit(5))
        for l in leaves:
            l["_id"] = str(l["_id"])
            l["studentId"] = str(l["studentId"])
            l["startDate"] = l["startDate"].isoformat()
            l["endDate"] = l["endDate"].isoformat()
            l["appliedDate"] = l["appliedDate"].isoformat()
            if l.get("approvedBy"):
                l["approvedBy"] = str(l["approvedBy"])
                
        # Fetch absentee history
        absences = list(db.absentees.find({"studentId": student_id}).sort("date", -1).limit(5))
        for a in absences:
            a["_id"] = str(a["_id"])
            a["studentId"] = str(a["studentId"])
            a["date"] = a["date"].isoformat()
            if a.get("markedBy"):
                a["markedBy"] = str(a["markedBy"])
                
        return {
            "role": "Student",
            "attendancePercentage": student.get("attendancePercentage", 100.0),
            "totalFine": student.get("totalFine", 0.0),
            "pendingLeavesCount": pending_leaves,
            "unexcusedAbsencesCount": unexcused_count,
            "notifications": notifications,
            "recentLeaves": leaves,
            "recentAbsences": absences,
            "studentInfo": {
                "registerNo": student["registerNo"],
                "enrollNo": student["enrollNo"],
                "fullName": student["fullName"],
                "program": student["program"],
                "departmentName": student["departmentName"],
                "semester": student["semester"],
                "section": student["section"]
            }
        }
        
    # 2. Coordinator / HOD Dashboard Metrics
    elif role in ["Coordinator", "HOD"]:
        if not dept_id:
            raise HTTPException(status_code=400, detail="Staff user is not assigned to a department")
            
        # Get total students in department
        total_students = db.students.count_documents({"departmentId": dept_id})
        
        # Calculate average attendance
        pipeline = [
            {"$match": {"departmentId": dept_id}},
            {"$group": {"_id": None, "avg_att": {"$avg": "$attendancePercentage"}}}
        ]
        result = list(db.students.aggregate(pipeline))
        avg_attendance = result[0]["avg_att"] if result else 100.0
        
        # Find low attendance count (< 75%)
        low_att_count = db.students.count_documents({
            "departmentId": dept_id,
            "attendancePercentage": {"$lt": 75.0}
        })
        
        # Find pending leave applications for department students
        dept_student_ids = [s["_id"] for s in db.students.find({"departmentId": dept_id}, {"_id": 1})]
        pending_leaves = db.leaveApplications.count_documents({
            "studentId": {"$in": dept_student_ids},
            "status": "Pending"
        })
        
        # Retrieve list of students with low attendance
        low_att_students = list(db.students.find({
            "departmentId": dept_id,
            "attendancePercentage": {"$lt": 75.0}
        }).sort("attendancePercentage", 1))
        
        for s in low_att_students:
            s["_id"] = str(s["_id"])
            s["userId"] = str(s["userId"])
            s["departmentId"] = str(s["departmentId"])
            
        # Retrieve list of pending leave applications
        pending_leave_list = list(db.leaveApplications.find({
            "studentId": {"$in": dept_student_ids},
            "status": "Pending"
        }).sort("appliedDate", -1))
        
        for l in pending_leave_list:
            l["_id"] = str(l["_id"])
            # Fetch student name
            student_rec = db.students.find_one({"_id": l["studentId"]}, {"fullName": 1, "registerNo": 1})
            if student_rec:
                l["studentName"] = student_rec["fullName"]
                l["registerNo"] = student_rec["registerNo"]
            l["studentId"] = str(l["studentId"])
            l["startDate"] = l["startDate"].isoformat()
            l["endDate"] = l["endDate"].isoformat()
            l["appliedDate"] = l["appliedDate"].isoformat()
            
        return {
            "role": role,
            "totalStudents": total_students,
            "averageAttendance": round(avg_attendance, 2) if avg_attendance else 0,
            "lowAttendanceCount": low_att_count,
            "pendingLeavesCount": pending_leaves,
            "lowAttendanceStudents": low_att_students,
            "pendingLeaves": pending_leave_list
        }
        
    # 3. Dean Dashboard Metrics
    elif role == "Dean":
        # Dean has visibility across all departments
        total_students = db.students.count_documents({})

        # Calculate overall average attendance
        pipeline = [
            {"$group": {"_id": None, "avg_att": {"$avg": "$attendancePercentage"}}}
        ]
        result = list(db.students.aggregate(pipeline))
        avg_attendance = result[0]["avg_att"] if result else 100.0

        # Overall low attendance
        low_att_count = db.students.count_documents({"attendancePercentage": {"$lt": 75.0}})

        # Overall pending leaves
        pending_leaves = db.leaveApplications.count_documents({"status": "Pending"})

        # --- BUG FIX: Replaced N+1 per-department loop with a single aggregation ---
        dept_agg_pipeline = [
            {
                "$group": {
                    "_id": "$departmentId",
                    "totalStudents": {"$sum": 1},
                    "averageAttendance": {"$avg": "$attendancePercentage"}
                }
            }
        ]
        dept_agg_results = {
            str(r["_id"]): r
            for r in db.students.aggregate(dept_agg_pipeline)
            if r["_id"] is not None
        }

        depts = list(db.departments.find({}))
        dept_stats = []
        for d in depts:
            dept_id_str = str(d["_id"])
            agg = dept_agg_results.get(dept_id_str, {})
            dept_stats.append({
                "id": dept_id_str,
                "departmentCode": d["departmentCode"],
                "departmentName": d["departmentName"],
                "totalStudents": agg.get("totalStudents", 0),
                "averageAttendance": round(agg.get("averageAttendance", 0.0), 2)
            })

        return {
            "role": "Dean",
            "totalStudents": total_students,
            "averageAttendance": round(avg_attendance, 2),
            "lowAttendanceCount": low_att_count,
            "pendingLeavesCount": pending_leaves,
            "departments": dept_stats
        }
        
    else:
        # Faculty or Admin (fallback)
        return {"role": role, "message": f"Metrics loaded for {role}."}

