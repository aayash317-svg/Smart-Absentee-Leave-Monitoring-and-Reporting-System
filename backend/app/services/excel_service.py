"""
Excel report generation service.
Uses openpyxl (if available) or standard CSV format simulation to write Excel sheets.
"""
import io
import logging

logger = logging.getLogger("app")

def generate_attendance_excel(report_data: dict) -> io.BytesIO:
    """
    Generate an Excel sheet of student attendance.
    Returns a BytesIO stream of the Excel workbook.
    """
    buffer = io.BytesIO()
    
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Summary"
        
        # Style Definitions
        title_font = Font(name="Calibri", size=16, bold=True, color="1A365D")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center")
        
        # Title
        ws.merge_cells("A1:E1")
        ws["A1"] = f"Attendance Report - {report_data.get('departmentName', 'All Departments')}"
        ws["A1"].font = title_font
        ws.row_dimensions[1].height = 40
        
        # Headers
        headers = ["Student Name", "Register No", "Year", "Semester", "Attendance Percentage"]
        ws.append([]) # Empty row 2
        ws.append(headers) # Row 3
        ws.row_dimensions[3].height = 25
        
        # Header style
        for col_idx in range(1, 6):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            
        # Data
        for s in report_data.get("students", []):
            ws.append([
                s.get("fullName", ""),
                s.get("registerNo", ""),
                s.get("year", ""),
                s.get("semester", ""),
                s.get("attendancePercentage", 100.0) / 100.0  # Decimal form for percentage formatting
            ])
            
        # Format percentage column (E)
        for r in range(4, ws.max_row + 1):
            cell = ws.cell(row=r, column=5)
            cell.number_format = '0.0%'
            cell.alignment = center_align
            
        wb.save(buffer)
    except ImportError:
        # Fallback to CSV formatted text if openpyxl is not installed
        logger.warning("openpyxl library not installed, generating CSV fallback")
        buffer.write(b"Student Name,Register No,Year,Semester,Attendance Percentage\n")
        for s in report_data.get("students", []):
            line = f"{s.get('fullName')},{s.get('registerNo')},{s.get('year')},{s.get('semester')},{s.get('attendancePercentage')}%\n"
            buffer.write(line.encode("utf-8"))
            
    buffer.seek(0)
    return buffer
