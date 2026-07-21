"""
Report compilation service.
Provides a class-based interface used by dean and hod routes to generate Excel/PDF reports.
Fetches attendance data from MongoDB and delegates to excel_service and pdf_service.
"""
import datetime
import io
from bson.objectid import ObjectId
from ..database.connection import get_db
from .excel_service import generate_attendance_excel
from .pdf_service import generate_attendance_pdf


class ReportService:
    """Orchestrates report generation for department or institution-wide data."""

    @classmethod
    async def _compile_data(cls, department_id: str = None) -> dict:
        """
        Query MongoDB (async) and compile student data for report generation.
        """
        db = get_db()
        dept_name = "All Departments"
        query = {}

        if department_id:
            try:
                dept_obj_id = ObjectId(department_id) if isinstance(department_id, str) else department_id
                query["$or"] = [
                    {"departmentId": dept_obj_id},
                    {"departmentId": str(department_id)}
                ]
                dept = await db.departments.find_one({"_id": dept_obj_id})
                if not dept:
                    dept = await db.departments.find_one({"_id": str(department_id)})
                if dept:
                    dept_name = dept.get("departmentName", dept.get("name", "Department Report"))
                else:
                    dept_name = f"Department ({department_id})"
            except Exception:
                query["departmentId"] = str(department_id)

        students = await db.students.find(query).sort("fullName", 1).to_list(length=1000)
        students_list = [
            {
                "fullName": s.get("fullName", s.get("name", "Student")),
                "registerNo": s.get("registerNo", s.get("register_number", "")),
                "enrollNo": s.get("enrollNo", f"ENR-{s.get('registerNo', '')}"),
                "year": s.get("year", 1),
                "semester": s.get("semester", 1),
                "attendancePercentage": float(s.get("attendancePercentage", 100.0)),
            }
            for s in students
        ]

        return {
            "departmentName": dept_name,
            "generatedAt": datetime.datetime.utcnow().strftime("%d-%b-%Y %I:%M %p UTC"),
            "students": students_list,
        }

    @classmethod
    async def get_institution_excel(cls) -> bytes:
        """Generate institution-wide Excel attendance report. Returns raw bytes."""
        data = await cls._compile_data(department_id=None)
        buf: io.BytesIO = generate_attendance_excel(data)
        return buf.read()

    @classmethod
    async def get_department_excel(cls, department_id: str) -> bytes:
        """Generate department-specific Excel attendance report. Returns raw bytes."""
        data = await cls._compile_data(department_id=department_id)
        buf: io.BytesIO = generate_attendance_excel(data)
        return buf.read()

    @classmethod
    async def get_institution_pdf(cls) -> bytes:
        """Generate institution-wide PDF attendance report. Returns raw bytes."""
        data = await cls._compile_data(department_id=None)
        buf: io.BytesIO = generate_attendance_pdf(data)
        return buf.read()

    @classmethod
    async def get_department_pdf(cls, department_id: str) -> bytes:
        """Generate department-specific PDF attendance report. Returns raw bytes."""
        data = await cls._compile_data(department_id=department_id)
        buf: io.BytesIO = generate_attendance_pdf(data)
        return buf.read()


def get_report_file(format_type: str, department_id: str = None):
    """
    Functional helper — fetches data and returns (stream, media_type, filename).
    Used outside the class context if needed.
    """
    data = ReportService._compile_data(department_id)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d")
    if format_type.lower() == "pdf":
        return (
            generate_attendance_pdf(data),
            "application/pdf",
            f"attendance_report_{ts}.pdf",
        )
    return (
        generate_attendance_excel(data),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        f"attendance_report_{ts}.xlsx",
    )
