import datetime
from bson import ObjectId

async def process_attendance_notifications(db, student: dict, old_att: float, new_att: float):
    student_userId = student.get("userId")
    if not student_userId:
        return
        
    student_name = student.get("fullName", student.get("name", "Student"))
    reg_no = student.get("registerNo", student.get("register_number", ""))
    
    # Identify student's department code
    dept_code = student.get("department", "")
    if not dept_code:
        dept_name = student.get("departmentName", "")
        if "Computer Science" in dept_name or "CSE" in dept_name:
            dept_code = "CSE"
        elif "Data Science" in dept_name or "AIDS" in dept_name or "AI&DS" in dept_name:
            dept_code = "AI&DS"
        elif "Machine Learning" in dept_name or "AIML" in dept_name or "AI&ML" in dept_name:
            dept_code = "AI&ML"

    # Find the coordinator's user document
    coord_user = None
    coord_id = student.get("coordinator_id")
    if coord_id:
        coord_user = await db.users.find_one({"id_number": coord_id})
    if not coord_user and dept_code:
        coord_user = await db.users.find_one({"role": "Coordinator", "department": dept_code})

    # Find the HOD's user document by department
    hod_user = None
    if dept_code:
        hod_user = await db.users.find_one({"role": "HOD", "department": dept_code})

    # 1. 75% -> Warning Notification (Student)
    if new_att < 75.0 and old_att >= 75.0:
        await db.notifications.insert_one({
            "notification_id": f"NT_WARN_{int(new_att)}_{ObjectId()}",
            "student_id": student.get("id", "ST_UNKNOWN"),
            "recipientId": ObjectId(student_userId) if isinstance(student_userId, str) else student_userId,
            "title": "Low Attendance Alert (75%)",
            "message": f"Your attendance has dropped to {new_att}%, which is below the warning threshold of 75%. Please contact your coordinator.",
            "type": "Student",
            "is_read": False,
            "isRead": False,
            "createdAt": datetime.datetime.utcnow(),
            "created_at": datetime.datetime.utcnow().isoformat()
        })

    # 2. 70% -> Parent Notification (logged to student)
    if new_att < 70.0 and old_att >= 70.0:
        await db.notifications.insert_one({
            "notification_id": f"NT_PAR_{int(new_att)}_{ObjectId()}",
            "student_id": student.get("id", "ST_UNKNOWN"),
            "recipientId": ObjectId(student_userId) if isinstance(student_userId, str) else student_userId,
            "title": "Parent Alert (70%)",
            "message": f"Parent Notification: Your attendance is critically low at {new_att}%. An automated alert has been sent to your registered parent contact.",
            "type": "Student",
            "is_read": False,
            "isRead": False,
            "createdAt": datetime.datetime.utcnow(),
            "created_at": datetime.datetime.utcnow().isoformat()
        })

    # 3. 65% -> Coordinator Notification
    if new_att < 65.0 and old_att >= 65.0:
        if coord_user:
            await db.notifications.insert_one({
                "notification_id": f"NT_COORD_{int(new_att)}_{ObjectId()}",
                "student_id": student.get("id", "ST_UNKNOWN"),
                "recipientId": coord_user["_id"],
                "title": "Low Attendance Alert (65%)",
                "message": f"Coordinator Alert: Student {student_name} ({reg_no}) attendance has dropped to {new_att}%.",
                "type": "Coordinator",
                "is_read": False,
                "isRead": False,
                "createdAt": datetime.datetime.utcnow(),
                "created_at": datetime.datetime.utcnow().isoformat()
            })

    # 4. 60% -> Defaulter List
    if new_att < 60.0 and old_att >= 60.0:
        await db.notifications.insert_one({
            "notification_id": f"NT_DEF_{int(new_att)}_{ObjectId()}",
            "student_id": student.get("id", "ST_UNKNOWN"),
            "recipientId": ObjectId(student_userId) if isinstance(student_userId, str) else student_userId,
            "title": "Defaulter List Alert (60%)",
            "message": f"Defaulter List Alert: You have been added to the Defaulter List. Your attendance has dropped to {new_att}% (under 60%).",
            "type": "Student",
            "is_read": False,
            "isRead": False,
            "createdAt": datetime.datetime.utcnow(),
            "created_at": datetime.datetime.utcnow().isoformat()
        })

    # 5. Below 50% -> HOD Notification
    if new_att < 50.0 and old_att >= 50.0:
        if hod_user:
            await db.notifications.insert_one({
                "notification_id": f"NT_HOD_{int(new_att)}_{ObjectId()}",
                "student_id": student.get("id", "ST_UNKNOWN"),
                "recipientId": hod_user["_id"],
                "title": "Critical Attendance Alert (<50%)",
                "message": f"HOD Alert: Student {student_name} ({reg_no}) attendance has critically dropped to {new_att}%.",
                "type": "HOD",
                "is_read": False,
                "isRead": False,
                "createdAt": datetime.datetime.utcnow(),
                "created_at": datetime.datetime.utcnow().isoformat()
            })
