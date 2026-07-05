# MongoDB Schema

## users
- _id (ObjectId)
- fullName
- email
- phone
- password
- role
- departmentId
- status
- createdAt
- updatedAt

## departments
- _id
- departmentCode
- departmentName
- program
- hodId
- coordinatorId
- totalStudents
- createdAt

## students
- _id
- registerNo
- enrollNo
- fullName
- program
- departmentName
- userId
- departmentId
- year
- semester
- section
- attendancePercentage
- totalFine
- createdAt

## Other collections
- absentees
- leaveApplications
- fineRules
- finePayments
- notifications
- auditLogs
- reports
(Fields follow the validation rules created in MongoDB Compass.)
