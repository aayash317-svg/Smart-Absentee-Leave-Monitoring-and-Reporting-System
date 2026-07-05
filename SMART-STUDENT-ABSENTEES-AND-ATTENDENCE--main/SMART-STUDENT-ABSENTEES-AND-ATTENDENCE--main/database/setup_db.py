import datetime
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId

def setup():
    print("Connecting to MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    
    # Drop database to start fresh
    print("Re-creating database: smart_absentee_db...")
    client.drop_database("smart_absentee_db")
    db = client.smart_absentee_db
    
    # 1. Create Collections
    collections = [
        'users', 'departments', 'students', 'absentees', 
        'leaveApplications', 'fineRules', 'finePayments', 
        'notifications', 'auditLogs', 'reports'
    ]
    for col in collections:
        db.create_collection(col)
        print(f"Created collection: {col}")
        
    # 2. Create Indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("phone", unique=True)
    db.users.create_index("role")
    db.students.create_index("registerNo", unique=True)
    db.students.create_index("enrollNo", unique=True)
    db.finePayments.create_index("receiptNo", unique=True, sparse=True)
    print("Indexes created.")
    
    # 3. Create Password Hashes
    password_bytes = b"password123"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # 4. Insert Departments
    dept_ids = {
        "CSE": ObjectId(),
        "ECE": ObjectId(),
        "MECH": ObjectId()
    }
    
    # 5. Insert Users for Staff
    dean_id = ObjectId()
    hod_cse_id = ObjectId()
    coord_cse_id = ObjectId()
    faculty_cse_id = ObjectId()
    
    users = [
        {
            "_id": dean_id,
            "fullName": "Dr. Sarah Jenkins",
            "email": "dean@university.edu",
            "phone": "9876543210",
            "password": hashed_password,
            "role": "Dean",
            "departmentId": None,
            "status": "Active",
            "createdAt": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        },
        {
            "_id": hod_cse_id,
            "fullName": "Dr. Ramesh Kumar",
            "email": "hod_cse@university.edu",
            "phone": "9876543211",
            "password": hashed_password,
            "role": "HOD",
            "departmentId": dept_ids["CSE"],
            "status": "Active",
            "createdAt": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        },
        {
            "_id": coord_cse_id,
            "fullName": "Prof. Amit Sharma",
            "email": "coord_cse@university.edu",
            "phone": "9876543212",
            "password": hashed_password,
            "role": "Coordinator",
            "departmentId": dept_ids["CSE"],
            "status": "Active",
            "createdAt": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        },
        {
            "_id": faculty_cse_id,
            "fullName": "Dr. Sunita Rao",
            "email": "faculty_cse@university.edu",
            "phone": "9876543213",
            "password": hashed_password,
            "role": "Faculty",
            "departmentId": dept_ids["CSE"],
            "status": "Active",
            "createdAt": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        }
    ]
    
    # 6. Create Student Users & Records
    student_data = [
        ("John Doe", "CSE202401", "EN2401", "CSE", 3, 5, "A", 68.5, 400.0),
        ("Jane Smith", "CSE202402", "EN2402", "CSE", 3, 5, "B", 78.0, 0.0),
        ("Bob Johnson", "ECE202401", "EN2403", "ECE", 2, 3, "A", 55.0, 1200.0),
        ("Alice Brown", "ECE202402", "EN2404", "ECE", 2, 3, "A", 88.5, 0.0),
        ("Charlie Green", "MECH202401", "EN2405", "MECH", 4, 7, "A", 74.0, 100.0)
    ]
    
    students_list = []
    for i, (name, reg, enroll, dept, year, sem, sec, att, fine) in enumerate(student_data):
        u_id = ObjectId()
        s_id = ObjectId()
        email = f"student{i+1}@university.edu"
        phone = f"987654322{i}"
        
        users.append({
            "_id": u_id,
            "fullName": name,
            "email": email,
            "phone": phone,
            "password": hashed_password,
            "role": "Student",
            "departmentId": dept_ids[dept],
            "status": "Active",
            "createdAt": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        })
        
        students_list.append({
            "_id": s_id,
            "registerNo": reg,
            "enrollNo": enroll,
            "fullName": name,
            "program": "B.Tech",
            "departmentName": f"Department of {dept}",
            "userId": u_id,
            "departmentId": dept_ids[dept],
            "year": year,
            "semester": sem,
            "section": sec,
            "attendancePercentage": float(att),
            "totalFine": float(fine),
            "createdAt": datetime.datetime.now()
        })
        
    db.users.insert_many(users)
    db.students.insert_many(students_list)
    print("Users and Students inserted.")
    
    # 7. Insert Departments records
    departments = [
        {
            "_id": dept_ids["CSE"],
            "departmentCode": "CSE",
            "departmentName": "Computer Science & Engineering",
            "program": "B.Tech",
            "hodId": hod_cse_id,
            "coordinatorId": coord_cse_id,
            "totalStudents": 2,
            "createdAt": datetime.datetime.now()
        },
        {
            "_id": dept_ids["ECE"],
            "departmentCode": "ECE",
            "departmentName": "Electronics & Communication Engineering",
            "program": "B.Tech",
            "hodId": None,
            "coordinatorId": None,
            "totalStudents": 2,
            "createdAt": datetime.datetime.now()
        },
        {
            "_id": dept_ids["MECH"],
            "departmentCode": "MECH",
            "departmentName": "Mechanical Engineering",
            "program": "B.Tech",
            "hodId": None,
            "coordinatorId": None,
            "totalStudents": 1,
            "createdAt": datetime.datetime.now()
        }
    ]
    db.departments.insert_many(departments)
    print("Departments inserted.")
    
    # Get student object ids
    john_id = students_list[0]["_id"]
    jane_id = students_list[1]["_id"]
    bob_id = students_list[2]["_id"]
    charlie_id = students_list[4]["_id"]
    
    # 8. Absentees Seeding
    absentees = [
        {
            "studentId": john_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=5),
            "reason": "Fever",
            "status": "Excused",
            "markedBy": faculty_cse_id,
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": john_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=4),
            "reason": "Fever",
            "status": "Excused",
            "markedBy": faculty_cse_id,
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": john_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=1),
            "reason": "Bunked class",
            "status": "Unexcused",
            "markedBy": faculty_cse_id,
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": bob_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=10),
            "reason": "Personal",
            "status": "Unexcused",
            "markedBy": coord_cse_id,
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": bob_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=9),
            "reason": "Personal",
            "status": "Unexcused",
            "markedBy": coord_cse_id,
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": charlie_id,
            "date": datetime.datetime.now() - datetime.timedelta(days=2),
            "reason": "Family function",
            "status": "Unexcused",
            "markedBy": coord_cse_id,
            "createdAt": datetime.datetime.now()
        }
    ]
    db.absentees.insert_many(absentees)
    print("Absentees inserted.")
    
    # 9. Leave Applications Seeding
    leave_apps = [
        {
            "studentId": john_id,
            "startDate": datetime.datetime.now() - datetime.timedelta(days=5),
            "endDate": datetime.datetime.now() - datetime.timedelta(days=4),
            "leaveType": "Sick Leave",
            "reason": "Suffering from viral fever. Doctor advised 2 days rest.",
            "status": "Approved",
            "approvedBy": coord_cse_id,
            "appliedDate": datetime.datetime.now() - datetime.timedelta(days=6),
            "updatedAt": datetime.datetime.now()
        },
        {
            "studentId": john_id,
            "startDate": datetime.datetime.now() + datetime.timedelta(days=2),
            "endDate": datetime.datetime.now() + datetime.timedelta(days=3),
            "leaveType": "Casual Leave",
            "reason": "Attending sister's wedding.",
            "status": "Pending",
            "approvedBy": None,
            "appliedDate": datetime.datetime.now(),
            "updatedAt": datetime.datetime.now()
        },
        {
            "studentId": jane_id,
            "startDate": datetime.datetime.now() - datetime.timedelta(days=1),
            "endDate": datetime.datetime.now() - datetime.timedelta(days=1),
            "leaveType": "Duty Leave",
            "reason": "Representing university in hackathon.",
            "status": "Approved",
            "approvedBy": coord_cse_id,
            "appliedDate": datetime.datetime.now() - datetime.timedelta(days=3),
            "updatedAt": datetime.datetime.now()
        }
    ]
    db.leaveApplications.insert_many(leave_apps)
    print("Leave applications inserted.")
    
    # 10. Fine Rules
    fine_rules = [
        {
            "minAttendance": 75.0,
            "fineAmountPerDay": 100.0,
            "graceDays": 3,
            "createdAt": datetime.datetime.now()
        }
    ]
    db.fineRules.insert_many(fine_rules)
    print("Fine rules inserted.")
    
    # 11. Fine Payments
    fine_payments = [
        {
            "studentId": john_id,
            "amount": 400.0,
            "paymentDate": datetime.datetime.now(),
            "paymentMode": "Online",
            "status": "Paid",
            "receiptNo": "REC-CSE-2026-001",
            "createdAt": datetime.datetime.now()
        },
        {
            "studentId": bob_id,
            "amount": 1200.0,
            "paymentDate": datetime.datetime.now() - datetime.timedelta(days=15),
            "paymentMode": "Online",
            "status": "Pending",
            "receiptNo": "REC-ECE-2026-002",
            "createdAt": datetime.datetime.now()
        }
    ]
    db.finePayments.insert_many(fine_payments)
    print("Fine payments inserted.")
    
    # 12. Notifications
    notifications = [
        {
            "recipientId": students_list[0]["userId"], # John Doe user
            "title": "Low Attendance Warning",
            "message": "Your attendance is 68.5%, which is below the required 75%. Please submit leave documents or contact your coordinator.",
            "type": "Warning",
            "isRead": False,
            "createdAt": datetime.datetime.now()
        },
        {
            "recipientId": students_list[0]["userId"], # John Doe user
            "title": "Leave Application Approved",
            "message": "Your Sick Leave application for dates 30-Jun to 01-Jul has been approved.",
            "type": "Leave Status",
            "isRead": True,
            "createdAt": datetime.datetime.now()
        },
        {
            "recipientId": students_list[2]["userId"], # Bob Johnson user
            "title": "Fine Payment Overdue",
            "message": "You have a pending attendance fine of Rs. 1200. Please clear it immediately to avoid block in hall tickets.",
            "type": "Fine Alert",
            "isRead": False,
            "createdAt": datetime.datetime.now()
        }
    ]
    db.notifications.insert_many(notifications)
    print("Notifications inserted.")
    
    print("\nDatabase initialization complete! 5 student records and staff seeded.")
    print("Default password for all users is: password123")

if __name__ == "__main__":
    setup()
