// Create indexes for smart_absentee_db
db = db.getSiblingDB('smart_absentee_db');

// users collection indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ phone: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ departmentId: 1 });

// students collection indexes
db.students.createIndex({ registerNo: 1 }, { unique: true });
db.students.createIndex({ enrollNo: 1 }, { unique: true });
db.students.createIndex({ userId: 1 });
db.students.createIndex({ departmentId: 1 });

// absentees collection indexes
db.absentees.createIndex({ studentId: 1 });
db.absentees.createIndex({ date: 1 });

// leaveApplications collection indexes
db.leaveApplications.createIndex({ studentId: 1 });
db.leaveApplications.createIndex({ status: 1 });

// finePayments collection indexes
db.finePayments.createIndex({ studentId: 1 });
db.finePayments.createIndex({ receiptNo: 1 }, { unique: true, sparse: true });

// notifications collection indexes
db.notifications.createIndex({ recipientId: 1 });
db.notifications.createIndex({ isRead: 1 });

// auditLogs collection indexes
db.auditLogs.createIndex({ userId: 1 });
db.auditLogs.createIndex({ createdAt: -1 });

print("All database indexes created successfully.");
