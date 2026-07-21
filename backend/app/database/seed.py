import asyncio
import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import settings
from ..core.password import hash_password

async def seed_db():
    print(f"Connecting to MongoDB: {settings.MONGO_DB_NAME}...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]

    # ── Clear existing collections ────────────────────────────────────────────
    print("Clearing existing sample data...")
    for col in ["users", "students", "departments", "leaves", "fines",
                "attendance_logs", "notifications", "audit_logs", "sms_logs",
                "leaveApplications", "absentees"]:
        await db[col].delete_many({})

    # ── 1. Departments ────────────────────────────────────────────────────────
    print("Seeding 3 Departments...")
    dept_cs_id  = ObjectId()
    dept_aids_id = ObjectId()
    dept_aiml_id = ObjectId()

    departments = [
        {"_id": dept_cs_id,  "departmentName": "Computer Science & Engineering", "departmentCode": "CSE", "createdAt": datetime.datetime.utcnow()},
        {"_id": dept_aids_id, "departmentName": "Artificial Intelligence & Data Science", "departmentCode": "AI&DS", "createdAt": datetime.datetime.utcnow()},
        {"_id": dept_aiml_id, "departmentName": "Artificial Intelligence & Machine Learning", "departmentCode": "AI&ML", "createdAt": datetime.datetime.utcnow()},
    ]
    await db.departments.insert_many(departments)

    # ── 2. Staff Users ────────────────────────────────────────────────────────
    print("Seeding Staff Users (Admin, Dean, 3 HODs, 3 Coordinators)...")
    
    admin_hash = hash_password("Admin@2026")
    dean_hash = hash_password("Dean@2026")
    hod_hash = hash_password("Hod@2026")
    cc_hash = hash_password("CC@2026")

    admin_user_id = ObjectId()
    dean_user_id = ObjectId()
    
    hod_cs_uid = ObjectId()
    hod_aids_uid = ObjectId()
    hod_aiml_uid = ObjectId()

    cc_cs_uid = ObjectId()
    cc_aids_uid = ObjectId()
    cc_aiml_uid = ObjectId()

    staff_users = [
        # Admin
        {
            "_id": admin_user_id,
            "id_number": "ADMIN001",
            "email": "admin@takshashilauniv.ac.in",
            "fullName": "Super Admin",
            "phone": "+91-99999-00000",
            "password": admin_hash,
            "role": "Admin",
            "status": "Active",
            "departmentId": None,
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        # Dean
        {
            "_id": dean_user_id,
            "id_number": "DEAN001",
            "email": "dean@takshashilauniv.ac.in",
            "fullName": "Dr. Rajesh Kumar",
            "phone": "+91-99001-00001",
            "password": dean_hash,
            "role": "Dean",
            "status": "Active",
            "departmentId": None,
            "department": "ALL",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        # HODs
        {
            "_id": hod_cs_uid,
            "id_number": "HOD001",
            "email": "hod.cse@takshashilauniv.ac.in",
            "fullName": "Dr. Arun Kumar",
            "phone": "+91-99001-00002",
            "password": hod_hash,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "department": "CSE",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_aids_uid,
            "id_number": "HOD002",
            "email": "hod.aids@takshilauniv.ac.in", # Using user's specific email address
            "fullName": "Dr. Surya Prakash",
            "phone": "+91-99001-00003",
            "password": hod_hash,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_aids_id),
            "department": "AI&DS",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_aiml_uid,
            "id_number": "HOD003",
            "email": "hod.aiml@takshashilauniv.ac.in",
            "fullName": "Dr. Ramesh Kumar",
            "phone": "+91-99001-00004",
            "password": hod_hash,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_aiml_id),
            "department": "AI&ML",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        # Coordinators
        {
            "_id": cc_cs_uid,
            "id_number": "CC001",
            "email": "cc.cse@takshashilauniv.ac.in",
            "fullName": "Mr. Karthikeyan",
            "phone": "+91-99001-00005",
            "password": cc_hash,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "department": "CSE",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        {
            "_id": cc_aids_uid,
            "id_number": "CC002",
            "email": "cc.aids@takshashilauniv.ac.in",
            "fullName": "Mrs. Priyadharshini",
            "phone": "+91-99001-00006",
            "password": cc_hash,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_aids_id),
            "department": "AI&DS",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        },
        {
            "_id": cc_aiml_uid,
            "id_number": "CC003",
            "email": "cc.aiml@takshashilauniv.ac.in",
            "fullName": "Mr. Arun Kumar",
            "phone": "+91-99001-00007",
            "password": cc_hash,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_aiml_id),
            "department": "AI&ML",
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": "",
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        }
    ]
    await db.users.insert_many(staff_users)

    # ── 3. Students (15 Records) ──────────────────────────────────────────────
    print("Seeding 15 Students...")
    
    students_raw = [
        # CSE Students
        ("ST001", "23CSE001", "Arjun Kumar",   "student.cse1@takshashilauniv.ac.in", dept_cs_id,   "CSE",   "CC001", 84.5),
        ("ST002", "23CSE002", "Hari Prasad",   "student.cse2@takshashilauniv.ac.in", dept_cs_id,   "CSE",   "CC001", 76.2),
        ("ST003", "23CSE003", "Vignesh Kumar", "student.cse3@takshashilauniv.ac.in", dept_cs_id,   "CSE",   "CC001", 73.5), # Warn
        ("ST004", "23CSE004", "Ajay Kumar",    "student.cse4@takshashilauniv.ac.in", dept_cs_id,   "CSE",   "CC001", 64.0), # Defaulter
        ("ST005", "23CSE005", "Kavin Raj",     "student.cse5@takshashilauniv.ac.in", dept_cs_id,   "CSE",   "CC001", 48.0), # Critical HOD
        # AI&DS Students
        ("ST101", "23AIDS001", "Ayash M",       "student.aids1@takshashilauniv.ac.in", dept_aids_id, "AI&DS", "CC002", 78.0),
        ("ST102", "23AIDS002", "Ranjith Kumar", "student.aids2@takshashilauniv.ac.in", dept_aids_id, "AI&DS", "CC002", 91.0),
        ("ST103", "23AIDS003", "Abinaya S",     "student.aids3@takshashilauniv.ac.in", dept_aids_id, "AI&DS", "CC002", 68.5), # Coord alert
        ("ST104", "23AIDS004", "Naveen Raj",    "student.aids4@takshashilauniv.ac.in", dept_aids_id, "AI&DS", "CC002", 55.0), # Critical HOD
        ("ST105", "23AIDS005", "Karthika P",    "student.aids5@takshashilauniv.ac.in", dept_aids_id, "AI&DS", "CC002", 82.0),
        # AI&ML Students
        ("ST201", "23AIML001", "Ashwin Kumar", "student.aiml1@takshashilauniv.ac.in", dept_aiml_id, "AI&ML", "CC003", 89.2),
        ("ST202", "23AIML002", "Vishal Kumar", "student.aiml2@takshashilauniv.ac.in", dept_aiml_id, "AI&ML", "CC003", 72.0), # Parent alert
        ("ST203", "23AIML003", "Monica S",     "student.aiml3@takshashilauniv.ac.in", dept_aiml_id, "AI&ML", "CC003", 61.5), # Defaulter
        ("ST204", "23AIML004", "Hariharan",    "student.aiml4@takshashilauniv.ac.in", dept_aiml_id, "AI&ML", "CC003", 95.0),
        ("ST205", "23AIML005", "Priyanka R",    "student.aiml5@takshashilauniv.ac.in", dept_aiml_id, "AI&ML", "CC003", 44.5), # HOD alert
    ]

    student_users = []
    student_profiles = []
    
    student_profile_ids = {} 
    student_user_ids = {} 

    for id_num, reg_no, name, email, dept_oid, dept_code, cc_id, att in students_raw:
        s_uid = ObjectId()
        s_poid = ObjectId()
        
        student_profile_ids[id_num] = s_poid
        student_user_ids[id_num] = s_uid
        
        s_hash = hash_password(reg_no) 

        student_users.append({
            "_id": s_uid,
            "id_number": id_num,
            "register_number": reg_no,
            "email": email,
            "fullName": name,
            "phone": "+91-90001-00000",
            "password": s_hash,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_oid),
            "department": dept_code,
            "coordinator_id": cc_id,
            "is_active": True,
            "is_verified": True,
            "last_login": "",
            "attendance_percentage": str(att),
            "profile_image": "",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        })

        student_profiles.append({
            "_id": s_poid,
            "userId": str(s_uid),
            "id": id_num,
            "fullName": name,
            "name": name,
            "registerNo": reg_no,
            "register_number": reg_no,
            "enrollNo": f"ENR-{reg_no}",
            "program": "B.Tech",
            "departmentId": str(dept_oid),
            "departmentName": f"Department of {dept_code}",
            "department": dept_code,
            "coordinator_id": cc_id,
            "year": 3,
            "semester": 5,
            "section": "A",
            "attendancePercentage": att,
            "totalClasses": 100,
            "classesAttended": int(att),
            "totalFine": 20.0 if id_num == "ST101" else 0.0,
            "createdAt": datetime.datetime.utcnow()
        })

    await db.users.insert_many(student_users)
    await db.students.insert_many(student_profiles)

    # ── 4. Leave Applications (20 Records) ────────────────────────────────────
    print("Seeding 20 Leave Records...")
    today = datetime.datetime.utcnow()
    
    leaves = []
    leave_types = ["Full Day", "Half Day", "Sick Leave", "Medical Leave"]
    reasons = ["Fever", "Family wedding", "Vomiting", "Eye checkup", "Travel"]
    
    st_keys = list(student_profile_ids.keys()) 
    
    for i in range(20):
        st_key = st_keys[i % len(st_keys)]
        st_poid = student_profile_ids[st_key]
        st_uid = student_user_ids[st_key]
        
        st_name = next(s["fullName"] for s in student_profiles if s["_id"] == st_poid)
        st_reg = next(s["registerNo"] for s in student_profiles if s["_id"] == st_poid)
        st_dept = next(s["department"] for s in student_profiles if s["_id"] == st_poid)
        st_dept_id = next(s["departmentId"] for s in student_profiles if s["_id"] == st_poid)
        st_cc = next(s["coordinator_id"] for s in student_profiles if s["_id"] == st_poid)
        
        days_ago = i + 1
        start_date = today - datetime.timedelta(days=days_ago)
        end_date = start_date 
        
        status_val = "Pending"
        if i < 10:
            status_val = "Approved"
        elif i < 15:
            status_val = "Rejected"
            
        fine_amount = 0.0
        delay = (i % 3)
        applied_date = start_date + datetime.timedelta(days=delay)
        if delay == 1:
            fine_amount = 10.0
        elif delay == 2:
            fine_amount = 20.0
            
        l_doc = {
            "_id": ObjectId(),
            "leave_id": f"LV{i+1:03d}",
            "student_id": st_key,
            "studentId": st_poid,
            "name": st_name,
            "studentName": st_name,
            "register_no": st_reg,
            "registerNo": st_reg,
            "department": st_dept,
            "departmentName": f"Department of {st_dept}",
            "departmentId": ObjectId(st_dept_id),
            "leave_type": leave_types[i % len(leave_types)],
            "leaveType": leave_types[i % len(leave_types)],
            "reason": reasons[i % len(reasons)],
            "status": status_val,
            "coordinator_id": st_cc,
            "fine": str(int(fine_amount)),
            "calculatedFine": fine_amount,
            "delayDays": delay,
            "startDate": start_date,
            "endDate": end_date,
            "appliedDate": applied_date,
            "approvedBy": cc_aids_uid if status_val == "Approved" else None,
            "created_at": start_date.isoformat(),
            "updated_at": today.isoformat(),
            "createdAt": start_date,
            "updatedAt": today
        }
        leaves.append(l_doc)
        
    await db.leaveApplications.insert_many(leaves)
    await db.leaves.insert_many(leaves)

    # ── 5. Notifications (20 Records) ─────────────────────────────────────────
    print("Seeding 20 Notifications...")
    notifications = []
    
    for i in range(20):
        st_key = st_keys[i % len(st_keys)]
        st_uid = student_user_ids[st_key]
        
        n_doc = {
            "notification_id": f"NT{i+1:03d}",
            "student_id": st_key,
            "recipientId": st_uid,
            "title": "Leave Approved" if i % 2 == 0 else "Low Attendance Warning",
            "message": "Your leave has been approved." if i % 2 == 0 else "Your attendance is dropping. Please check.",
            "is_read": False,
            "isRead": False,
            "type": "Student",
            "createdAt": today - datetime.timedelta(hours=i),
            "created_at": (today - datetime.timedelta(hours=i)).isoformat()
        }
        notifications.append(n_doc)
        
    await db.notifications.insert_many(notifications)

    # ── 6. Attendance Logs / Absentees (15 Records) ───────────────────────────
    print("Seeding 15 Attendance / Absentee Records...")
    absentee_logs = []
    
    for i in range(15):
        st_key = st_keys[i % len(st_keys)]
        st_poid = student_profile_ids[st_key]
        st_reg = next(s["registerNo"] for s in student_profiles if s["_id"] == st_poid)
        st_name = next(s["fullName"] for s in student_profiles if s["_id"] == st_poid)
        st_dept = next(s["department"] for s in student_profiles if s["_id"] == st_poid)
        st_dept_id = next(s["departmentId"] for s in student_profiles if s["_id"] == st_poid)
        st_cc = next(s["coordinator_id"] for s in student_profiles if s["_id"] == st_poid)
        
        marker_uid = cc_aids_uid
        if st_dept == "CSE":
            marker_uid = cc_cs_uid
        elif st_dept == "AI&ML":
            marker_uid = cc_aiml_uid

        a_doc = {
            "student_id": st_key,
            "studentId": st_poid,
            "registerNo": st_reg,
            "register_no": st_reg,
            "fullName": st_name,
            "department": st_dept,
            "departmentId": ObjectId(st_dept_id),
            "date": today - datetime.timedelta(days=i+2),
            "hour": (i % 6) + 1,
            "subject": "Core Course " + str((i % 3) + 1),
            "markedBy": marker_uid,
            "status": "Absent" if i % 3 != 0 else "Excused",
            "attendance": "74" if i == 0 else "80",
            "leaveApproved": i % 3 == 0,
            "createdAt": today - datetime.timedelta(days=i+2)
        }
        absentee_logs.append(a_doc)
        
    await db.attendance_logs.insert_many(absentee_logs)
    await db.absentees.insert_many(absentee_logs)

    # ── 7. Fine Records (10 Records) ──────────────────────────────────────────
    print("Seeding 10 Fine Records...")
    fines = []
    
    for i in range(10):
        st_key = st_keys[i % len(st_keys)]
        st_poid = student_profile_ids[st_key]
        st_name = next(s["fullName"] for s in student_profiles if s["_id"] == st_poid)
        st_dept_id = next(s["departmentId"] for s in student_profiles if s["_id"] == st_poid)
        
        f_doc = {
            "fine_id": f"FN{i+1:03d}",
            "student_id": st_key,
            "studentId": st_poid,
            "studentName": st_name,
            "departmentId": ObjectId(st_dept_id),
            "days_delayed": str((i % 4) + 1),
            "amount": float(((i % 4) + 1) * 10.0),
            "reason": f"Late leave submission ({((i % 4) + 1)} days delay)",
            "status": "Pending" if i % 2 == 0 else "Paid",
            "receiptNo": f"REC-SS-2026-{i+100:03d}" if i % 2 != 0 else None,
            "paymentDate": today - datetime.timedelta(days=1) if i % 2 != 0 else None,
            "createdAt": today - datetime.timedelta(days=i+3)
        }
        fines.append(f_doc)
        
    await db.fines.insert_many(fines)

    # ── 8. System Settings ────────────────────────────────────────────────────
    print("Updating System Settings...")
    await db.settings.update_one({"key": "system"}, {"$set": {
        "key": "system",
        "attendanceThreshold": 75,
        "finePerDay": 50,
        "smsSendEnabled": True,
        "emailSendEnabled": True,
        "gracePeriodDays": 0,
        "maxLeavePerSemester": 15,
        "updatedAt": datetime.datetime.utcnow()
    }}, upsert=True)

    # ── 9. Audit Logs ─────────────────────────────────────────────────────────
    print("Seeding Audit Logs...")
    audit_logs = [
        {"userId": cc_cs_uid, "action": "Mark Absent", "details": "Marked ST001 absent for Core Course 1", "createdAt": datetime.datetime.utcnow()},
        {"userId": cc_aids_uid, "action": "Mark Absent", "details": "Marked ST101 absent for Core Course 2", "createdAt": datetime.datetime.utcnow()},
        {"userId": dean_user_id, "action": "Report Generated", "details": "Dean generated institution-wide Excel report", "createdAt": datetime.datetime.utcnow()}
    ]
    await db.audit_logs.insert_many(audit_logs)

    client.close()
    print("\n[OK] Seeding completed successfully!")
    print("\n===========================================================")
    print("  LOGIN CREDENTIALS FOR DEMO")
    print("===========================================================")
    print("  Admin         : admin@takshashilauniv.ac.in | Admin@2026")
    print("  Dean          : dean@takshashilauniv.ac.in  | Dean@2026")
    print("  HOD (CSE)     : hod.cse@takshashilauniv.ac.in | Hod@2026")
    print("  HOD (AI&DS)   : hod.aids@takshashilauniv.ac.in | Hod@2026")
    print("  HOD (AI&ML)   : hod.aiml@takshashilauniv.ac.in | Hod@2026")
    print("  CC (AI&DS)    : cc.aids@takshashilauniv.ac.in | CC@2026")
    print("  Student (AI&DS): 23AIDS001                    | 23AIDS001")
    print("===========================================================\n")

if __name__ == "__main__":
    asyncio.run(seed_db())
