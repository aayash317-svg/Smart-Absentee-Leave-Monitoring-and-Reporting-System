import asyncio
import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import settings
from ..core.password import hash_password

async def seed_db():
    print(f"Connecting to MongoDB database: {settings.MONGO_DB_NAME}...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]

    # Clean existing collections
    print("Clearing existing sample data...")
    collections_to_clear = ["users", "students", "departments", "leaves", "fines", "attendance_logs"]
    for col in collections_to_clear:
        await db[col].delete_many({})

    # 1. Seed Departments
    print("Seeding Departments...")
    dept_cs_id = ObjectId()
    dept_it_id = ObjectId()
    
    departments = [
        {
            "_id": dept_cs_id,
            "departmentName": "Computer Science & Engineering",
            "code": "CSE",
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": dept_it_id,
            "departmentName": "Information Technology",
            "code": "IT",
            "createdAt": datetime.datetime.utcnow()
        }
    ]
    await db.departments.insert_many(departments)

    # Common Hashed Password for all seed users: "Pass123!"
    hashed_password = hash_password("Pass123!")

    # 2. Seed Users (Dean, HODs, Coordinators, Students)
    print("Seeding Users...")
    dean_id = ObjectId()
    hod_cs_id = ObjectId()
    hod_it_id = ObjectId()
    coord_cs_id = ObjectId()
    coord_it_id = ObjectId()
    student_cs1_user_id = ObjectId()
    student_cs2_user_id = ObjectId()
    student_it1_user_id = ObjectId()
    student_it2_user_id = ObjectId()

    users = [
        {
            "_id": dean_id,
            "email": "dean@college.edu",
            "fullName": "Dr. Sarah Jenkins",
            "phone": "+19998887771",
            "password": hashed_password,
            "role": "Dean",
            "status": "Active",
            "departmentId": None,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_cs_id,
            "email": "hod.cs@college.edu",
            "fullName": "Dr. Alan Turing",
            "phone": "+19998887772",
            "password": hashed_password,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": hod_it_id,
            "email": "hod.it@college.edu",
            "fullName": "Dr. Tim Berners-Lee",
            "phone": "+19998887773",
            "password": hashed_password,
            "role": "HOD",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": coord_cs_id,
            "email": "coord.cs@college.edu",
            "fullName": "Grace Hopper",
            "phone": "+19998887774",
            "password": hashed_password,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": coord_it_id,
            "email": "coord.it@college.edu",
            "fullName": "Ada Lovelace",
            "phone": "+19998887775",
            "password": hashed_password,
            "role": "Coordinator",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_cs1_user_id,
            "email": "student.cs1@college.edu",
            "fullName": "John Doe",
            "phone": "+19998887776",
            "password": hashed_password,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_cs2_user_id,
            "email": "student.cs2@college.edu",
            "fullName": "Jane Smith",
            "phone": "+19998887777",
            "password": hashed_password,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_cs_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_it1_user_id,
            "email": "student.it1@college.edu",
            "fullName": "Aayash A",
            "phone": "+19998887778",
            "password": hashed_password,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_it2_user_id,
            "email": "student.it2@college.edu",
            "fullName": "Bob Wilson",
            "phone": "+19998887779",
            "password": hashed_password,
            "role": "Student",
            "status": "Active",
            "departmentId": str(dept_it_id),
            "createdAt": datetime.datetime.utcnow()
        }
    ]
    await db.users.insert_many(users)

    # 3. Seed Students Metadata
    print("Seeding Student profiles...")
    student_cs1_id = ObjectId()
    student_cs2_id = ObjectId()
    student_it1_id = ObjectId()
    student_it2_id = ObjectId()

    students = [
        {
            "_id": student_cs1_id,
            "userId": str(student_cs1_user_id),
            "fullName": "John Doe",
            "registerNo": "REG2026CSE01",
            "enrollNo": "ENR2026CSE01",
            "program": "B.E. Computer Science",
            "departmentId": str(dept_cs_id),
            "departmentName": "Computer Science & Engineering",
            "year": 3,
            "semester": 6,
            "section": "A",
            "attendancePercentage": 90.0,
            "totalClasses": 50,
            "classesAttended": 45,
            "totalFine": 0.0,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_cs2_id,
            "userId": str(student_cs2_user_id),
            "fullName": "Jane Smith",
            "registerNo": "REG2026CSE02",
            "enrollNo": "ENR2026CSE02",
            "program": "B.E. Computer Science",
            "departmentId": str(dept_cs_id),
            "departmentName": "Computer Science & Engineering",
            "year": 3,
            "semester": 6,
            "section": "B",
            "attendancePercentage": 74.0,
            "totalClasses": 50,
            "classesAttended": 37,
            "totalFine": 40.0,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_it1_id,
            "userId": str(student_it1_user_id),
            "fullName": "Aayash A",
            "registerNo": "REG2026IT01",
            "enrollNo": "ENR2026IT01",
            "program": "B.Tech Information Technology",
            "departmentId": str(dept_it_id),
            "departmentName": "Information Technology",
            "year": 3,
            "semester": 6,
            "section": "A",
            "attendancePercentage": 96.0,
            "totalClasses": 50,
            "classesAttended": 48,
            "totalFine": 0.0,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "_id": student_it2_id,
            "userId": str(student_it2_user_id),
            "fullName": "Bob Wilson",
            "registerNo": "REG2026IT02",
            "enrollNo": "ENR2026IT02",
            "program": "B.Tech Information Technology",
            "departmentId": str(dept_it_id),
            "departmentName": "Information Technology",
            "year": 3,
            "semester": 6,
            "section": "A",
            "attendancePercentage": 60.0,
            "totalClasses": 50,
            "classesAttended": 30,
            "totalFine": 120.0,
            "createdAt": datetime.datetime.utcnow()
        }
    ]
    await db.students.insert_many(students)

    # 4. Seed Attendance/Absence Logs
    print("Seeding Attendance Logs...")
    today = datetime.datetime.utcnow().date()
    yesterday = today - datetime.timedelta(days=1)
    two_days_ago = today - datetime.timedelta(days=2)

    absentee_logs = [
        # Jane Smith absent yesterday & 2 days ago
        {
            "studentId": str(student_cs2_id),
            "registerNo": "REG2026CSE02",
            "fullName": "Jane Smith",
            "departmentId": str(dept_cs_id),
            "date": datetime.datetime.combine(yesterday, datetime.time.min),
            "hour": 2,
            "subject": "Distributed Systems",
            "markedBy": "Grace Hopper",
            "status": "Absent",
            "leaveApproved": False,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "studentId": str(student_cs2_id),
            "registerNo": "REG2026CSE02",
            "fullName": "Jane Smith",
            "departmentId": str(dept_cs_id),
            "date": datetime.datetime.combine(two_days_ago, datetime.time.min),
            "hour": 4,
            "subject": "Theory of Computation",
            "markedBy": "Grace Hopper",
            "status": "Absent",
            "leaveApproved": False,
            "createdAt": datetime.datetime.utcnow()
        },
        # Bob Wilson absent today & yesterday
        {
            "studentId": str(student_it2_id),
            "registerNo": "REG2026IT02",
            "fullName": "Bob Wilson",
            "departmentId": str(dept_it_id),
            "date": datetime.datetime.combine(today, datetime.time.min),
            "subject": "Mobile Computing",
            "hour": 1,
            "markedBy": "Ada Lovelace",
            "status": "Absent",
            "leaveApproved": False,
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "studentId": str(student_it2_id),
            "registerNo": "REG2026IT02",
            "fullName": "Bob Wilson",
            "departmentId": str(dept_it_id),
            "date": datetime.datetime.combine(yesterday, datetime.time.min),
            "subject": "Software Engineering",
            "hour": 3,
            "markedBy": "Ada Lovelace",
            "status": "Absent",
            "leaveApproved": False,
            "createdAt": datetime.datetime.utcnow()
        }
    ]
    await db.attendance_logs.insert_many(absentee_logs)

    # 5. Seed Sample Leave Applications
    print("Seeding Leave Applications...")
    leaves = [
        {
            "studentId": str(student_cs2_id),
            "studentName": "Jane Smith",
            "departmentId": str(dept_cs_id),
            "leaveType": "Sick Leave",
            "reason": "Severe fever and doctor-advised rest.",
            "startDate": datetime.datetime.combine(yesterday, datetime.time.min),
            "endDate": datetime.datetime.combine(yesterday, datetime.time.max),
            "submittedAt": datetime.datetime.utcnow() - datetime.timedelta(hours=12),
            "status": "Pending",
            "delayDays": 1,
            "calculatedFine": 10.0,
            "attachments": []
        },
        {
            "studentId": str(student_it2_id),
            "studentName": "Bob Wilson",
            "departmentId": str(dept_it_id),
            "leaveType": "Medical Leave",
            "reason": "Dental surgery appointment.",
            "startDate": datetime.datetime.combine(two_days_ago, datetime.time.min),
            "endDate": datetime.datetime.combine(two_days_ago, datetime.time.max),
            "submittedAt": datetime.datetime.utcnow() - datetime.timedelta(days=1),
            "status": "Approved",
            "delayDays": 2,
            "calculatedFine": 20.0,
            "attachments": []
        }
    ]
    await db.leaves.insert_many(leaves)

    # 6. Seed Sample Fine Payments
    print("Seeding Fines...")
    fines = [
        {
            "studentId": str(student_cs2_id),
            "studentName": "Jane Smith",
            "amount": 40.0,
            "reason": "Late leave submission (2 days delay)",
            "status": "Unpaid",
            "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=3)
        },
        {
            "studentId": str(student_it2_id),
            "studentName": "Bob Wilson",
            "amount": 120.0,
            "reason": "Late leave submission (4 days delay with extra weekend charge)",
            "status": "Unpaid",
            "createdAt": datetime.datetime.utcnow() - datetime.timedelta(days=2)
        }
    ]
    await db.fines.insert_many(fines)

    print("\nSeeding completed successfully!")
    print("\nCredentials for testing (Password for all accounts is: Pass123!):")
    print(" - Dean: dean@college.edu")
    print(" - HOD (Computer Science): hod.cs@college.edu")
    print(" - HOD (Information Technology): hod.it@college.edu")
    print(" - Coordinator (CS): coord.cs@college.edu")
    print(" - Coordinator (IT): coord.it@college.edu")
    print(" - Student (CS): student.cs1@college.edu")
    print(" - Student (IT): student.it1@college.edu")

if __name__ == "__main__":
    asyncio.run(seed_db())
