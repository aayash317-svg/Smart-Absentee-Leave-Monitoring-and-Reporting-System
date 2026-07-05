// Seed data for smart_absentee_db
db = db.getSiblingDB('smart_absentee_db');

// Clear existing records
db.users.deleteMany({});
db.departments.deleteMany({});
db.students.deleteMany({});
db.absentees.deleteMany({});
db.leaveApplications.deleteMany({});
db.fineRules.deleteMany({});
db.finePayments.deleteMany({});
db.notifications.deleteMany({});

// Generate common ObjectIds
const deptCseId = ObjectId();
const deptEceId = ObjectId();
const deptMechId = ObjectId();

const deanId = ObjectId();
const hodCseId = ObjectId();
const coordCseId = ObjectId();
const facultyCseId = ObjectId();

const johnUserId = ObjectId();
const johnStudentId = ObjectId();
const janeUserId = ObjectId();
const janeStudentId = ObjectId();
const bobUserId = ObjectId();
const bobStudentId = ObjectId();

// Hashed password for 'password123'
const mockPasswordHash = "$2b$12$R9h/lIPzNgb.aSCESi.O2.2S2tZzP9yLhE1bWv8FjZ.0OaVn2fD2m";

// Insert departments
db.departments.insertMany([
  {
    _id: deptCseId,
    departmentCode: "CSE",
    departmentName: "Computer Science & Engineering",
    program: "B.Tech",
    hodId: hodCseId,
    coordinatorId: coordCseId,
    totalStudents: NumberInt(2),
    createdAt: new Date()
  },
  {
    _id: deptEceId,
    departmentCode: "ECE",
    departmentName: "Electronics & Communication Engineering",
    program: "B.Tech",
    hodId: null,
    coordinatorId: null,
    totalStudents: NumberInt(1),
    createdAt: new Date()
  }
]);

// Insert staff users
db.users.insertMany([
  {
    _id: deanId,
    fullName: "Dr. Sarah Jenkins",
    email: "dean@university.edu",
    phone: "9876543210",
    password: mockPasswordHash,
    role: "Dean",
    departmentId: null,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    _id: hodCseId,
    fullName: "Dr. Ramesh Kumar",
    email: "hod_cse@university.edu",
    phone: "9876543211",
    password: mockPasswordHash,
    role: "HOD",
    departmentId: deptCseId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    _id: coordCseId,
    fullName: "Prof. Amit Sharma",
    email: "coord_cse@university.edu",
    phone: "9876543212",
    password: mockPasswordHash,
    role: "Coordinator",
    departmentId: deptCseId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    _id: facultyCseId,
    fullName: "Dr. Sunita Rao",
    email: "faculty_cse@university.edu",
    phone: "9876543213",
    password: mockPasswordHash,
    role: "Faculty",
    departmentId: deptCseId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  }
]);

// Insert student users
db.users.insertMany([
  {
    _id: johnUserId,
    fullName: "John Doe",
    email: "student1@university.edu",
    phone: "9876543220",
    password: mockPasswordHash,
    role: "Student",
    departmentId: deptCseId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    _id: janeUserId,
    fullName: "Jane Smith",
    email: "student2@university.edu",
    phone: "9876543221",
    password: mockPasswordHash,
    role: "Student",
    departmentId: deptCseId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    _id: bobUserId,
    fullName: "Bob Johnson",
    email: "student3@university.edu",
    phone: "9876543222",
    password: mockPasswordHash,
    role: "Student",
    departmentId: deptEceId,
    status: "Active",
    createdAt: new Date(),
    updatedAt: new Date()
  }
]);

// Insert students
db.students.insertMany([
  {
    _id: johnStudentId,
    registerNo: "CSE202401",
    enrollNo: "EN2401",
    fullName: "John Doe",
    program: "B.Tech",
    departmentName: "Department of Computer Science & Engineering",
    userId: johnUserId,
    departmentId: deptCseId,
    year: NumberInt(3),
    semester: NumberInt(5),
    section: "A",
    attendancePercentage: 68.5,
    totalFine: 400.0,
    createdAt: new Date()
  },
  {
    _id: janeStudentId,
    registerNo: "CSE202402",
    enrollNo: "EN2402",
    fullName: "Jane Smith",
    program: "B.Tech",
    departmentName: "Department of Computer Science & Engineering",
    userId: janeUserId,
    departmentId: deptCseId,
    year: NumberInt(3),
    semester: NumberInt(5),
    section: "B",
    attendancePercentage: 78.0,
    totalFine: 0.0,
    createdAt: new Date()
  },
  {
    _id: bobStudentId,
    registerNo: "ECE202401",
    enrollNo: "EN2403",
    fullName: "Bob Johnson",
    program: "B.Tech",
    departmentName: "Department of Electronics & Communication Engineering",
    userId: bobUserId,
    departmentId: deptEceId,
    year: NumberInt(2),
    semester: NumberInt(3),
    section: "A",
    attendancePercentage: 55.0,
    totalFine: 1200.0,
    createdAt: new Date()
  }
]);

// Insert absentees
db.absentees.insertMany([
  {
    studentId: johnStudentId,
    date: new Date(new Date().setDate(new Date().getDate() - 5)),
    reason: "Fever",
    status: "Excused",
    markedBy: facultyCseId,
    createdAt: new Date()
  },
  {
    studentId: johnStudentId,
    date: new Date(new Date().setDate(new Date().getDate() - 1)),
    reason: "Unexcused personal absence",
    status: "Unexcused",
    markedBy: facultyCseId,
    createdAt: new Date()
  },
  {
    studentId: bobStudentId,
    date: new Date(new Date().setDate(new Date().getDate() - 2)),
    reason: "Out of town",
    status: "Unexcused",
    markedBy: coordCseId,
    createdAt: new Date()
  }
]);

// Insert leave applications
db.leaveApplications.insertMany([
  {
    studentId: johnStudentId,
    startDate: new Date(new Date().setDate(new Date().getDate() - 5)),
    endDate: new Date(new Date().setDate(new Date().getDate() - 4)),
    leaveType: "Sick Leave",
    reason: "Suffering from viral fever. Doctor advised 2 days rest.",
    status: "Approved",
    approvedBy: coordCseId,
    appliedDate: new Date(new Date().setDate(new Date().getDate() - 6)),
    updatedAt: new Date()
  },
  {
    studentId: johnStudentId,
    startDate: new Date(new Date().setDate(new Date().getDate() + 2)),
    endDate: new Date(new Date().setDate(new Date().getDate() + 3)),
    leaveType: "Casual Leave",
    reason: "Attending sister's wedding.",
    status: "Pending",
    approvedBy: null,
    appliedDate: new Date(),
    updatedAt: new Date()
  }
]);

// Insert fine rules
db.fineRules.insertOne({
  minAttendance: 75.0,
  fineAmountPerDay: 100.0,
  graceDays: NumberInt(3),
  createdAt: new Date()
});

// Insert fine payments
db.finePayments.insertMany([
  {
    studentId: johnStudentId,
    amount: 400.0,
    paymentDate: new Date(),
    paymentMode: "Online",
    status: "Paid",
    receiptNo: "REC-CSE-2026-001"
  },
  {
    studentId: bobStudentId,
    amount: 1200.0,
    paymentDate: new Date(new Date().setDate(new Date().getDate() - 10)),
    paymentMode: "Online",
    status: "Pending",
    receiptNo: "REC-ECE-2026-002"
  }
]);

// Insert notifications
db.notifications.insertMany([
  {
    recipientId: johnUserId,
    title: "Low Attendance Warning",
    message: "Your attendance is 68.5%, which is below the required 75%. Please submit leave documents.",
    type: "Warning",
    isRead: false
  },
  {
    recipientId: bobUserId,
    title: "Fine Payment Overdue",
    message: "You have a pending attendance fine of Rs. 1200. Please clear it immediately.",
    type: "Fine Alert",
    isRead: false
  }
]);

print("Seeding complete for smart_absentee_db.");
