import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List, Dict, Any

class PDFService:
    @staticmethod
    def generate_attendance_report(
        student_name: str, 
        register_no: str, 
        department: str, 
        attendance_pct: float, 
        absences: List[Dict[str, Any]]
    ) -> bytes:
        """Generate a professional styled PDF report of student attendance and return as bytes."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            rightMargin=36, 
            leftMargin=36, 
            topMargin=36, 
            bottomMargin=36
        )
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=25
        )
        body_style = styles['Normal']
        bold_body_style = ParagraphStyle('BoldBody', parent=styles['Normal'], fontName='Helvetica-Bold')
        
        # Document Headers
        story.append(Paragraph("Smart Absentee Leave Monitoring System", title_style))
        story.append(Paragraph(f"Attendance Report — Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Student Info Metadata Table
        info_data = [
            [
                Paragraph("Student Name:", bold_body_style), Paragraph(student_name, body_style),
                Paragraph("Register No:", bold_body_style), Paragraph(register_no, body_style)
            ],
            [
                Paragraph("Department:", bold_body_style), Paragraph(department, body_style),
                Paragraph("Current Attendance:", bold_body_style), Paragraph(f"{attendance_pct:.2f}%", body_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[110, 160, 110, 160])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 25))
        
        # Absence History section
        story.append(Paragraph("Absence Record Details", styles['Heading2']))
        story.append(Spacer(1, 8))
        
        headers = ["#", "Date", "Status", "Reason / Reference ID"]
        table_data = [headers]
        
        for idx, abs_rec in enumerate(absences):
            date_val = abs_rec.get("date")
            if isinstance(date_val, datetime.datetime):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)[:10]
                
            status = abs_rec.get("status", "Unexcused")
            reason = abs_rec.get("reason") or "N/A"
            if abs_rec.get("leaveApplicationId"):
                reason += f" (Leave App: {str(abs_rec['leaveApplicationId'])})"
                
            table_data.append([
                str(idx + 1),
                date_str,
                status,
                reason
            ])
            
        history_table = Table(table_data, colWidths=[40, 100, 100, 300])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ]))
        story.append(history_table)
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
