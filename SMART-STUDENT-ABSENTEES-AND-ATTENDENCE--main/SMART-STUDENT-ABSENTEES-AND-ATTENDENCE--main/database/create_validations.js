// Apply collection schema validations for smart_absentee_db
db = db.getSiblingDB('smart_absentee_db');

// 1. users validation
db.runCommand({
  collMod: "users",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fullName", "email", "phone", "password", "role", "status"],
      properties: {
        fullName: { bsonType: "string", description: "Must be a string and is required" },
        email: { bsonType: "string", pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", description: "Must be a valid email address and is required" },
        phone: { bsonType: "string", description: "Must be a string and is required" },
        password: { bsonType: "string", description: "Must be a string containing hashed password and is required" },
        role: { enum: ["Admin", "Dean", "HOD", "Coordinator", "Student", "Faculty"], description: "Must be one of the specified roles and is required" },
        departmentId: { bsonType: ["objectId", "null"], description: "Optional reference to department" },
        status: { enum: ["Active", "Inactive"], description: "Must be Active or Inactive and is required" }
      }
    }
  }
});

// 2. departments validation
db.runCommand({
  collMod: "departments",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["departmentCode", "departmentName"],
      properties: {
        departmentCode: { bsonType: "string" },
        departmentName: { bsonType: "string" },
        program: { bsonType: "string" },
        hodId: { bsonType: ["objectId", "null"] },
        coordinatorId: { bsonType: ["objectId", "null"] },
        totalStudents: { bsonType: "int" }
      }
    }
  }
});

// 3. students validation
db.runCommand({
  collMod: "students",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["registerNo", "enrollNo", "fullName", "userId", "departmentId"],
      properties: {
        registerNo: { bsonType: "string" },
        enrollNo: { bsonType: "string" },
        fullName: { bsonType: "string" },
        program: { bsonType: "string" },
        departmentName: { bsonType: "string" },
        userId: { bsonType: "objectId" },
        departmentId: { bsonType: "objectId" },
        year: { bsonType: "int" },
        semester: { bsonType: "int" },
        section: { bsonType: "string" },
        attendancePercentage: { bsonType: "double" },
        totalFine: { bsonType: "double" }
      }
    }
  }
});

// 4. absentees validation
db.runCommand({
  collMod: "absentees",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["studentId", "date", "status"],
      properties: {
        studentId: { bsonType: "objectId" },
        date: { bsonType: "date" },
        reason: { bsonType: "string" },
        status: { enum: ["Unexcused", "Excused"] },
        markedBy: { bsonType: "objectId" }
      }
    }
  }
});

// 5. leaveApplications validation
db.runCommand({
  collMod: "leaveApplications",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["studentId", "startDate", "endDate", "leaveType", "status"],
      properties: {
        studentId: { bsonType: "objectId" },
        startDate: { bsonType: "date" },
        endDate: { bsonType: "date" },
        leaveType: { enum: ["Sick Leave", "Duty Leave", "Casual Leave", "Other"] },
        reason: { bsonType: "string" },
        status: { enum: ["Pending", "Approved", "Rejected"] },
        approvedBy: { bsonType: ["objectId", "null"] },
        appliedDate: { bsonType: "date" }
      }
    }
  }
});

// 6. fineRules validation
db.runCommand({
  collMod: "fineRules",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["minAttendance", "fineAmountPerDay"],
      properties: {
        minAttendance: { bsonType: "double" },
        fineAmountPerDay: { bsonType: "double" },
        graceDays: { bsonType: "int" }
      }
    }
  }
});

// 7. finePayments validation
db.runCommand({
  collMod: "finePayments",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["studentId", "amount", "paymentDate", "status"],
      properties: {
        studentId: { bsonType: "objectId" },
        amount: { bsonType: "double" },
        paymentDate: { bsonType: "date" },
        paymentMode: { enum: ["Online", "Cash"] },
        status: { enum: ["Paid", "Pending"] },
        receiptNo: { bsonType: "string" }
      }
    }
  }
});

// 8. notifications validation
db.runCommand({
  collMod: "notifications",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["recipientId", "title", "message", "type", "isRead"],
      properties: {
        recipientId: { bsonType: "objectId" },
        title: { bsonType: "string" },
        message: { bsonType: "string" },
        type: { enum: ["Warning", "Leave Status", "Fine Alert", "Info"] },
        isRead: { bsonType: "bool" }
      }
    }
  }
});

print("All database validation schemas applied successfully.");
