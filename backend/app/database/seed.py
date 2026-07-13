"""
Database seeder for Smart Absentee Leave Monitoring and Reporting System.
Run: python -m backend.app.database.seed
Password for ALL accounts: Pass123!
"""
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

    # ── Clear existing sample data ────────────────────────────────────────────
    print("Clearing existing sample data...")
    for col in ["users", "students", "departments", "leaves", "fines",
                "attendance_logs", "notifications", "audit_logs", "sms_logs",
                "leaveApplications", "absentees"]:
        await db[col].delete_many({})

    # ── 1. Departments ────────────────────────────────────────────────────────
    print("Seeding Departments...")
    dept_cs_id  = ObjectId()
    dept_it_id  = ObjectId()
    dept_ece_id = ObjectId()

    departments = [
        {"_id": dept_cs_id,  "departmentName": "Computer Science & Engineering",
         "code": "CSE", "createdAt": datetime.datetime.utcnow()},
        {"_id": dept_it_id,  "departmentName": "Information Technology",
         "code": "IT",  "createdAt": datetime.datetime.utcnow()},
        {"_id": dept_ece_id, "departmentName": "Electronics & Communication Engineering",
         "code": "ECE", "createdAt": datetime.datetime.utcnow()},
    ]
    await db.departments.insert_many(departments)

    # ── 2. Staff Users ────────────────────────────────────────────────────────
    print("Seeding Staff Users...")
    hashed = hash_password("Pass123!")

    dean_id      = ObjectId()
    hod_cs_id    = ObjectId()
    hod_it_id    = ObjectId()
    coord_cs_id  = ObjectId()
    coord_it_id  = ObjectId()

    staff_users = [
        {
            "_id": dean_id,
            "email": "dean@college.edu",
            "fullName": "Dr. Sarah Jenkins",
            "phone": "+91-99001-00001",
            "password": hashed,
            "role": "Dean",
            "status": "Active",
            "departmentId": None,
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_cs_id,
            "email": "hod.cs@college.edu",
            "fullName": "Dr. Alan Turing",
            "phone": "+91-99001-00002",
            "password": hashed,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_it_id,
            "email": "hod.it@college.edu",
            "fullName": "Dr. Tim Berners-Lee",
            "phone": "+91-99001-00003",
            "password": hashed,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": coord_cs_id,
            "email": "coord.cs@college.edu",
            "fullName": "Grace Hopper",
            "phone": "+91-99001-00004",
            "password": hashed,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": coord_it_id,
            "email": "coord.it@college.edu",
            "fullName": "Ada Lovelace",
            "phone": "+91-99001-00005",
            "password": hashed,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        },
    ]
    await db.users.insert_many(staff_users)

    # ── 3. Student Users (10 students) ────────────────────────────────────────
    print("Seeding 10 Student Users...")

    # student user ids
    su = [ObjectId() for _ in range(10)]
    # student profile ids
    sp = [ObjectId() for _ in range(10)]

    # student raw data: (fullName, email, phone, dept_id, dept_name, program, year, sem, section, att%, fine, regNo, enrollNo)
    raw = [
        # CSE - 4 students
        ("Arjun Kumar",       "student.cs1@college.edu",  "+91-90001-00001", dept_cs_id, "Computer Science & Engineering", "B.E. Computer Science",  3, 6, "A", 92.0, 0.0,   "REG2026CSE01", "ENR2026CSE01"),
        ("Priya Sharma",      "student.cs2@college.edu",  "+91-90001-00002", dept_cs_id, "Computer Science & Engineering", "B.E. Computer Science",  3, 6, "A", 74.0, 40.0,  "REG2026CSE02", "ENR2026CSE02"),
        ("Rohan Patel",       "student.cs3@college.edu",  "+91-90001-00003", dept_cs_id, "Computer Science & Engineering", "B.E. Computer Science",  2, 4, "B", 88.0, 0.0,   "REG2026CSE03", "ENR2026CSE03"),
        ("Neha Verma",        "student.cs4@college.edu",  "+91-90001-00004", dept_cs_id, "Computer Science & Engineering", "B.E. Computer Science",  2, 4, "B", 65.0, 80.0,  "REG2026CSE04", "ENR2026CSE04"),
        # IT - 4 students
        ("Aayash A",          "student.it1@college.edu",  "+91-90001-00005", dept_it_id, "Information Technology",         "B.Tech Information Technology", 3, 6, "A", 96.0, 0.0,   "REG2026IT01", "ENR2026IT01"),
        ("Mohammed Salman",   "student.it2@college.edu",  "+91-90001-00006", dept_it_id, "Information Technology",         "B.Tech Information Technology", 3, 6, "A", 60.0, 120.0, "REG2026IT02", "ENR2026IT02"),
        ("Divya Nair",        "student.it3@college.edu",  "+91-90001-00007", dept_it_id, "Information Technology",         "B.Tech Information Technology", 2, 4, "B", 85.0, 0.0,   "REG2026IT03", "ENR2026IT03"),
        ("Karan Singh",       "student.it4@college.edu",  "+91-90001-00008", dept_it_id, "Information Technology",         "B.Tech Information Technology", 2, 4, "B", 70.0, 20.0,  "REG2026IT04", "ENR2026IT04"),
        # ECE - 2 students
        ("Sneha Reddy",       "student.ece1@college.edu", "+91-90001-00009", dept_ece_id,"Electronics & Communication Engineering", "B.E. ECE", 3, 6, "A", 91.0, 0.0,   "REG2026ECE01", "ENR2026ECE01"),
        ("Vikram Mehta",      "student.ece2@college.edu", "+91-90001-00010", dept_ece_id,"Electronics & Communication Engineering", "B.E. ECE", 1, 2, "A", 55.0, 200.0, "REG2026ECE02", "ENR2026ECE02"),
    ]

    student_user_docs = []
    student_profile_docs = []

    for i, (name, email, phone, dept_id, dept_name, program, year, sem, sec, att, fine, regNo, enrollNo) in enumerate(raw):
        total = 50
        attended = int(total * att / 100)

        student_user_docs.append({
            "_id": su[i],
            "email": email,
            "fullName": name,
            "phone": phone,
            "password": hashed,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_id),
            "failedLoginAttempts": 0,
            "lockoutUntil": None,
            "createdAt": datetime.datetime.utcnow()
        })

        student_profile_docs.append({
            "_id": sp[i],
            "userId": str(su[i]),
            "fullName": name,
            "registerNo": regNo,
            "enrollNo": enrollNo,
            "program": program,
            "departmentId": str(dept_id),
            "departmentName": dept_name,
            "year": year,
            "semester": sem,
            "section": sec,
            "attendancePercentage": att,
            "totalClasses": total,
            "classesAttended": attended,
            "totalFine": fine,
            "createdAt": datetime.datetime.utcnow()
        })

    await db.users.insert_many(student_user_docs)
    await db.students.insert_many(student_profile_docs)

    # ── 4. Absentee Logs ──────────────────────────────────────────────────────
    print("Seeding Attendance / Absentee Logs...")
    today     = datetime.datetime.utcnow().date()
    yesterday = today - datetime.timedelta(days=1)
    two_ago   = today - datetime.timedelta(days=2)
    three_ago = today - datetime.timedelta(days=3)

    def dt(d): return datetime.datetime.combine(d, datetime.time.min)

    absentee_logs = [
        # Priya (cs2) - low attendance
        {"studentId": str(sp[1]), "registerNo": "REG2026CSE02", "fullName": "Priya Sharma",
         "departmentId": str(dept_cs_id), "date": dt(yesterday), "hour": 2,
         "subject": "Distributed Systems", "markedBy": "Grace Hopper",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        {"studentId": str(sp[1]), "registerNo": "REG2026CSE02", "fullName": "Priya Sharma",
         "departmentId": str(dept_cs_id), "date": dt(two_ago), "hour": 4,
         "subject": "Theory of Computation", "markedBy": "Grace Hopper",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        # Neha (cs4) - low attendance
        {"studentId": str(sp[3]), "registerNo": "REG2026CSE04", "fullName": "Neha Verma",
         "departmentId": str(dept_cs_id), "date": dt(today), "hour": 1,
         "subject": "Software Design", "markedBy": "Grace Hopper",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        # Mohammed Salman (it2) - very low attendance
        {"studentId": str(sp[5]), "registerNo": "REG2026IT02", "fullName": "Mohammed Salman",
         "departmentId": str(dept_it_id), "date": dt(today), "hour": 1,
         "subject": "Mobile Computing", "markedBy": "Ada Lovelace",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        {"studentId": str(sp[5]), "registerNo": "REG2026IT02", "fullName": "Mohammed Salman",
         "departmentId": str(dept_it_id), "date": dt(yesterday), "hour": 3,
         "subject": "Software Engineering", "markedBy": "Ada Lovelace",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        # Karan (it4) - medium absence
        {"studentId": str(sp[7]), "registerNo": "REG2026IT04", "fullName": "Karan Singh",
         "departmentId": str(dept_it_id), "date": dt(two_ago), "hour": 2,
         "subject": "Database Management", "markedBy": "Ada Lovelace",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
        # Vikram (ece2) - very low
        {"studentId": str(sp[9]), "registerNo": "REG2026ECE02", "fullName": "Vikram Mehta",
         "departmentId": str(dept_ece_id), "date": dt(three_ago), "hour": 1,
         "subject": "Signal Processing", "markedBy": "Dr. Sarah Jenkins",
         "status": "Absent", "leaveApproved": False, "createdAt": datetime.datetime.utcnow()},
    ]
    await db.attendance_logs.insert_many(absentee_logs)

    # Also insert into absentees collection (used by new API)
    await db.absentees.insert_many(absentee_logs)

    # ── 5. Leave Applications ─────────────────────────────────────────────────
    print("Seeding Leave Applications...")
    leaves = [
        {
            "studentId": str(sp[1]), "studentName": "Priya Sharma",
            "departmentId": str(dept_cs_id),
            "leaveType": "Sick Leave",
            "reason": "Severe fever, doctor-advised bed rest.",
            "startDate": dt(yesterday), "endDate": dt(yesterday),
            "appliedDate": datetime.datetime.utcnow() - datetime.timedelta(hours=10),
            "status": "Pending", "delayDays": 1, "calculatedFine": 10.0,
            "certificateUrl": None, "attachments": []
        },
        {
            "studentId": str(sp[5]), "studentName": "Mohammed Salman",
            "departmentId": str(dept_it_id),
            "leaveType": "Medical Leave",
            "reason": "Dental surgery appointment.",
            "startDate": dt(two_ago), "endDate": dt(two_ago),
            "appliedDate": datetime.datetime.utcnow() - datetime.timedelta(days=1),
            "status": "Approved", "delayDays": 2, "calculatedFine": 20.0,
            "certificateUrl": None, "attachments": []
        },
        {
            "studentId": str(sp[3]), "studentName": "Neha Verma",
            "departmentId": str(dept_cs_id),
            "leaveType": "Emergency Leave",
            "reason": "Family emergency — travel required.",
            "startDate": dt(three_ago), "endDate": dt(yesterday),
            "appliedDate": datetime.datetime.utcnow() - datetime.timedelta(hours=5),
            "status": "Pending", "delayDays": 0, "calculatedFine": 0.0,
            "certificateUrl": None, "attachments": []
        },
        {
            "studentId": str(sp[9]), "studentName": "Vikram Mehta",
            "departmentId": str(dept_ece_id),
            "leaveType": "Personal Leave",
            "reason": "Sister's wedding ceremony.",
            "startDate": dt(three_ago), "endDate": dt(two_ago),
            "appliedDate": datetime.datetime.utcnow() - datetime.timedelta(days=4),
            "status": "Rejected", "delayDays": 1, "calculatedFine": 10.0,
            "certificateUrl": None, "attachments": []
        },
    ]
    await db.leaveApplications.insert_many(leaves)
    await db.leaves.insert_many(leaves)  # legacy alias

    # ── 6. Fines ──────────────────────────────────────────────────────────────
    print("Seeding Fines...")
    fines = [
        {"studentId": str(sp[1]), "studentName": "Priya Sharma",
         "departmentId": str(dept_cs_id), "amount": 40.0,
         "reason": "Late leave submission (2 days delay)", "status": "Unpaid",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=3)},
        {"studentId": str(sp[5]), "studentName": "Mohammed Salman",
         "departmentId": str(dept_it_id), "amount": 120.0,
         "reason": "Late leave submission (4 days delay with weekend surcharge)", "status": "Unpaid",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=2)},
        {"studentId": str(sp[3]), "studentName": "Neha Verma",
         "departmentId": str(dept_cs_id), "amount": 80.0,
         "reason": "Repeated unexcused absences", "status": "Unpaid",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=5)},
        {"studentId": str(sp[7]), "studentName": "Karan Singh",
         "departmentId": str(dept_it_id), "amount": 20.0,
         "reason": "Late leave submission (1 day delay)", "status": "Paid",
         "receiptNo": "REC-SS-2026-0042",
         "paymentDate": datetime.datetime.utcnow() - datetime.timedelta(days=1),
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=4)},
        {"studentId": str(sp[9]), "studentName": "Vikram Mehta",
         "departmentId": str(dept_ece_id), "amount": 200.0,
         "reason": "Low attendance penalty (below 60%)", "status": "Unpaid",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=1)},
    ]
    await db.fines.insert_many(fines)

    # ── 7. Notifications ──────────────────────────────────────────────────────
    print("Seeding Notifications...")
    notifs = [
        {"recipientId": su[1], "title": "Low Attendance Alert",
         "message": "Your attendance has dropped to 74.0%. Please contact your coordinator.",
         "type": "Student", "isRead": False, "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=2)},
        {"recipientId": su[3], "title": "Low Attendance Alert",
         "message": "Your attendance has dropped to 65.0%. You are at risk of detention.",
         "type": "Student", "isRead": False, "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=1)},
        {"recipientId": su[5], "title": "Leave Approved",
         "message": "Your Medical Leave from dental surgery on has been approved.",
         "type": "Student", "isRead": True,  "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=1)},
        {"recipientId": su[5], "title": "Low Attendance Alert",
         "message": "Your attendance is critically low at 60.0%. Immediate action required.",
         "type": "Student", "isRead": False, "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=3)},
        {"recipientId": su[9], "title": "Leave Rejected",
         "message": "Your Personal Leave application has been rejected. Please contact your HOD.",
         "type": "Student", "isRead": False, "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=6)},
    ]
    await db.notifications.insert_many(notifs)

    # ── 8. SMS Logs ───────────────────────────────────────────────────────────
    print("Seeding SMS Logs...")
    sms_logs = [
        {"recipient": "Priya Sharma", "phone": "+91-90001-00002",
         "message": "Alert: Your attendance is at 74.0%. Contact your coordinator.",
         "status": "Delivered", "sentAt": datetime.datetime.utcnow() - datetime.timedelta(hours=2)},
        {"recipient": "Mohammed Salman", "phone": "+91-90001-00006",
         "message": "Alert: Attendance critically low at 60.0%. Immediate action required.",
         "status": "Delivered", "sentAt": datetime.datetime.utcnow() - datetime.timedelta(hours=3)},
        {"recipient": "Vikram Mehta", "phone": "+91-90001-00010",
         "message": "Alert: Your leave application was rejected. Contact HOD.",
         "status": "Failed", "sentAt": datetime.datetime.utcnow() - datetime.timedelta(hours=6)},
    ]
    await db.sms_logs.insert_many(sms_logs)

    # ── 9. Audit Logs ─────────────────────────────────────────────────────────
    print("Seeding Audit Logs...")
    audit_logs = [
        {"userId": coord_cs_id, "action": "Mark Absent",
         "details": "Marked Priya Sharma absent for Distributed Systems",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=1)},
        {"userId": coord_it_id, "action": "Mark Absent",
         "details": "Marked Mohammed Salman absent for Mobile Computing",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=4)},
        {"userId": hod_cs_id,   "action": "Leave Approved",
         "details": "Approved leave for Mohammed Salman (Medical Leave)",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=22)},
        {"userId": hod_it_id,   "action": "Leave Rejected",
         "details": "Rejected leave for Vikram Mehta (Personal Leave)",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=6)},
        {"userId": dean_id,     "action": "Report Generated",
         "details": "Dean generated institution-wide Excel attendance report",
         "createdAt": datetime.datetime.utcnow() - datetime.timedelta(hours=8)},
    ]
    await db.audit_logs.insert_many(audit_logs)

    # ── System Settings ───────────────────────────────────────────────────────
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

    client.close()
    print("\n✅ Seeding completed successfully!")
    print("\n═══════════════════════════════════════════════════════════")
    print("  LOGIN CREDENTIALS — Password for ALL accounts: Pass123!")
    print("═══════════════════════════════════════════════════════════")
    print("  STAFF ACCOUNTS:")
    print("    Dean         : dean@college.edu")
    print("    HOD (CSE)    : hod.cs@college.edu")
    print("    HOD (IT)     : hod.it@college.edu")
    print("    Coord (CSE)  : coord.cs@college.edu")
    print("    Coord (IT)   : coord.it@college.edu")
    print("\n  STUDENT ACCOUNTS (10 students):")
    for _, email, _, _, dept_name, _, year, _, sec, att, fine, regNo, _ in raw:
        fine_str = f"  Fine: ₹{fine:.0f}" if fine > 0 else ""
        print(f"    {email:<35} Att: {att}%{fine_str}")
    print("═══════════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    asyncio.run(seed_db())
