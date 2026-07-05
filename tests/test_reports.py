import datetime
from backend.app.services.pdf_service import PDFService
from backend.app.services.excel_service import ExcelService

def test_pdf_report_generation():
    """Verify that PDFService compiles student logs into valid PDF binaries."""
    absences = [
        {"date": datetime.datetime(2026, 7, 1), "status": "Unexcused", "reason": "Slept in"},
        {"date": datetime.datetime(2026, 7, 2), "status": "Excused", "reason": "Family function", "leaveApplicationId": "65f4c568f12a34b5678cd90b"}
    ]
    pdf_bytes = PDFService.generate_attendance_report(
        student_name="Aayash A",
        register_no="REG20260705",
        department="Information Technology",
        attendance_pct=88.4,
        absences=absences
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # Verify standard PDF header magic bytes
    assert pdf_bytes.startswith(b"%PDF")

def test_excel_report_generation():
    """Verify that ExcelService formats student directories into standard OpenXML files."""
    students = [
        {
            "registerNo": "REG01", 
            "enrollNo": "ENR01", 
            "fullName": "Student One", 
            "program": "B.Tech IT", 
            "departmentName": "Information Technology", 
            "semester": 6, 
            "attendancePercentage": 92.5, 
            "totalFine": 0.0
        },
        {
            "registerNo": "REG02", 
            "enrollNo": "ENR02", 
            "fullName": "Student Two", 
            "program": "B.Tech CSE", 
            "departmentName": "Computer Science", 
            "semester": 4, 
            "attendancePercentage": 71.0, 
            "totalFine": 80.0
        }
    ]
    excel_bytes = ExcelService.generate_students_sheet(students)
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    # Verify ZIP file header magic bytes (Excel files are zip archives)
    assert excel_bytes.startswith(b"PK\x03\x04")
