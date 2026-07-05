# Database Documentation

## Project
Smart Absentee Leave Monitoring System

## Database
MongoDB (`smart_absentee_db`)

## Relationships
- departments -> users
- departments -> students
- users -> students
- students -> leaveApplications
- students -> absentees
- students -> finePayments
- students -> notifications
- users -> auditLogs
- users -> reports

## Indexes
Unique indexes were created on:
- users.email
- users.phone
- students.registerNo
- students.enrollNo
and supporting indexes for foreign keys and search fields.

## Validation
All collections use MongoDB JSON Schema validation.

## Sample Data
Five real student records were inserted together with realistic leave applications, attendance, fine payments, notifications, audit logs and reports.
