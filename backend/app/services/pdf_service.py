"""
PDF report generation service.
Uses reportlab (if available) or standard file operations to compile attendance reports.
"""
import io
import logging

logger = logging.getLogger("app")

def generate_attendance_pdf(report_data: dict) -> io.BytesIO:
    """
    Generate a PDF for student attendance summary.
    Returns a BytesIO binary stream of the PDF file.
    """
    buffer = io.BytesIO()
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=12
        )
        body_style = styles['Normal']
        
        # Header Info
        story.append(Paragraph(f"<b>Smart ERP - Student Attendance Report</b>", title_style))
        story.append(Paragraph(f"Generated on: {report_data.get('generatedAt', '')}", body_style))
        story.append(Paragraph(f"Department: {report_data.get('departmentName', 'All')}", body_style))
        story.append(Spacer(1, 15))
        
        # Table of Students
        table_data = [["Name", "Reg No", "Year", "Sem", "Attendance %"]]
        for s in report_data.get("students", []):
            table_data.append([
                s.get("fullName", ""),
                s.get("registerNo", ""),
                str(s.get("year", "")),
                str(s.get("semester", "")),
                f"{s.get('attendancePercentage', 100.0)}%"
            ])
            
        t = Table(table_data, colWidths=[150, 100, 50, 50, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        
        doc.build(story)
    except ImportError:
        # Fallback if reportlab is not installed (e.g. mock run during dependency install delay)
        logger.warning("reportlab library not installed, generating mock PDF content")
        buffer.write(b"%PDF-1.4 Mock PDF Attendance Report File\n")
        buffer.write(f"Report: {report_data.get('departmentName', 'All')}\n".encode())
        for s in report_data.get("students", []):
            buffer.write(f"{s.get('fullName')} - {s.get('attendancePercentage')}%\n".encode())
            
    buffer.seek(0)
    return buffer
