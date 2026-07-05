import datetime
from backend.app.services.pdf_service import generate_attendance_pdf
from backend.app.services.excel_service import generate_attendance_excel

def test_pdf_report_generation():
    """Verify that generate_attendance_pdf compiles student logs into valid PDF binaries."""
    report_data = {
        "departmentName": "Information Technology",
        "generatedAt": datetime.datetime.utcnow().strftime("%d-%b-%Y %I:%M %p UTC"),
        "students": [
            {
                "fullName": "Aayash A",
                "registerNo": "REG20260705",
                "year": 3,
                "semester": 6,
                "attendancePercentage": 88.4
            }
        ]
    }
    pdf_stream = generate_attendance_pdf(report_data)
    pdf_bytes = pdf_stream.getvalue()
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # Verify standard PDF header magic bytes
    assert pdf_bytes.startswith(b"%PDF")

def test_excel_report_generation():
    """Verify that generate_attendance_excel formats student directories into standard OpenXML files."""
    report_data = {
        "departmentName": "Information Technology",
        "generatedAt": datetime.datetime.utcnow().strftime("%d-%b-%Y %I:%M %p UTC"),
        "students": [
            {
                "fullName": "Student One",
                "registerNo": "REG01",
                "year": 3,
                "semester": 6,
                "attendancePercentage": 92.5
            }
        ]
    }
    excel_stream = generate_attendance_excel(report_data)
    excel_bytes = excel_stream.getvalue()
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    # Verify ZIP file header magic bytes (Excel files are zip archives)
    assert excel_bytes.startswith(b"PK\x03\x04")
