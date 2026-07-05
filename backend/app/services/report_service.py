import datetime
from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from ..database.connection import get_db
from .pdf_service import PDFService
from .excel_service import ExcelService

class ReportService:
    @staticmethod
    async def get_student_report_pdf(student_id: str) -> Optional[bytes]:
        """Aggregate database records for a student and generate a PDF attendance report."""
        db = get_db()
        
        # Verify student exists
        student = await db.students.find_one({"_id": ObjectId(student_id)})
        if not student:
            return None
            
        # Fetch all absence logs
        absences = []
        cursor = db.absentees.find({"studentId": ObjectId(student_id)}).sort("date", -1)
        async for doc in cursor:
            absences.append(doc)
            
        pdf_bytes = PDFService.generate_attendance_report(
            student_name=student["fullName"],
            register_no=student["registerNo"],
            department=student["departmentName"],
            attendance_pct=student.get("attendancePercentage", 100.0),
            absences=absences
        )
        return pdf_bytes

    @staticmethod
    async def get_department_excel(department_id: str) -> Optional[bytes]:
        """Fetch all students in a department and compile them into a formatted Excel sheet."""
        db = get_db()
        
        students = []
        cursor = db.students.find({"departmentId": ObjectId(department_id)}).sort("fullName", 1)
        async for doc in cursor:
            students.append(doc)
            
        excel_bytes = ExcelService.generate_students_sheet(students)
        return excel_bytes

    @staticmethod
    async def get_institution_excel() -> bytes:
        """Fetch all students institution-wide and compile them into a unified Excel directory."""
        db = get_db()
        
        students = []
        cursor = db.students.find({}).sort("departmentName", 1).sort("fullName", 1)
        async for doc in cursor:
            students.append(doc)
            
        excel_bytes = ExcelService.generate_students_sheet(students)
        return excel_bytes
