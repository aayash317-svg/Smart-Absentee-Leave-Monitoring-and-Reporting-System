"""
Report compilation service.
Fetches attendance statistics from MongoDB and coordinates PDF/Excel generation.
"""
import datetime
from ..database.connection import get_db
from .pdf_service import generate_attendance_pdf
from .excel_service import generate_attendance_excel

def compile_attendance_data(department_id: str = None) -> dict:
    """
    Query database and compile statistical data for reports.
    """
    db = get_db()
    
    query = {}
    dept_name = "All Departments"
    
    if department_id:
        from ..core.jwt import safe_object_id
        query["departmentId"] = safe_object_id(department_id)
        dept = db.departments.find_one({"_id": query["departmentId"]})
        if dept:
            dept_name = dept.get("departmentName", "Unknown Department")
            
    students = list(db.students.find(query).sort("fullName", 1))
    
    students_list = []
    for s in students:
        students_list.append({
            "id": str(s["_id"]),
            "fullName": s.get("fullName", ""),
            "registerNo": s.get("registerNo", ""),
            "enrollNo": s.get("enrollNo", ""),
            "year": s.get("year", 1),
            "semester": s.get("semester", 1),
            "attendancePercentage": s.get("attendancePercentage", 100.0)
        })
        
    return {
        "departmentName": dept_name,
        "generatedAt": datetime.datetime.utcnow().strftime("%d-%b-%Y %I:%M %p UTC"),
        "students": students_list
    }

def get_report_file(format_type: str, department_id: str = None):
    """
    Fetch raw attendance details and export to PDF or Excel binary streams.
    """
    data = compile_attendance_data(department_id)
    
    if format_type.lower() == "pdf":
        return generate_attendance_pdf(data), "application/pdf", f"attendance_report_{datetime.datetime.utcnow().strftime('%Y%m%d')}.pdf"
    else:
        return generate_attendance_excel(data), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"attendance_report_{datetime.datetime.utcnow().strftime('%Y%m%d')}.xlsx"
