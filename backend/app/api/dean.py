from fastapi import APIRouter, Depends, HTTPException, status, Response
from bson.objectid import ObjectId
from ..api.deps import get_current_user
from ..core.permissions import require_dean
from ..database.connection import get_db
from ..services.report_service import ReportService

router = APIRouter(prefix="/dean", tags=["dean"])

@router.get("/metrics")
async def get_institution_metrics(current_user: dict = Depends(get_current_user), _=Depends(require_dean)):
    """Fetch institution-wide metrics and comparative department stats."""
    db = get_db()
    total_students = await db.students.count_documents({})
    
    # Calculate average institution attendance percentage
    pipeline = [
        {"$group": {"_id": None, "avg_att": {"$avg": "$attendancePercentage"}}}
    ]
    result = []
    cursor = db.students.aggregate(pipeline)
    async for r in cursor:
        result.append(r)
    avg_attendance = result[0]["avg_att"] if result else 100.0
    
    low_att_count = await db.students.count_documents({"attendancePercentage": {"$lt": 75.0}})
    pending_leaves = await db.leaveApplications.count_documents({"status": "Pending"})
    
    # Compile per-department aggregates
    dept_agg_pipeline = [
        {
            "$group": {
                "_id": "$departmentId",
                "totalStudents": {"$sum": 1},
                "averageAttendance": {"$avg": "$attendancePercentage"}
            }
        }
    ]
    dept_stats_map = {}
    cursor = db.students.aggregate(dept_agg_pipeline)
    async for r in cursor:
        if r["_id"] is not None:
            dept_stats_map[str(r["_id"])] = r
            
    departments = await db.departments.find({}).to_list(length=100)
    dept_stats = []
    for d in departments:
        dept_id_str = str(d["_id"])
        agg = dept_stats_map.get(dept_id_str, {})
        dept_stats.append({
            "id": dept_id_str,
            "departmentCode": d["departmentCode"],
            "departmentName": d["departmentName"],
            "totalStudents": agg.get("totalStudents", 0),
            "averageAttendance": round(agg.get("averageAttendance", 0.0), 2)
        })
        
    return {
        "role": "Dean",
        "totalStudents": total_students,
        "averageAttendance": round(avg_attendance, 2),
        "lowAttendanceCount": low_att_count,
        "pendingLeavesCount": pending_leaves,
        "departments": dept_stats
    }

@router.get("/report/excel")
async def download_institution_report(current_user: dict = Depends(get_current_user), _=Depends(require_dean)):
    """Download the spreadsheet report representing the entire institution's directory."""
    excel_bytes = await ReportService.get_institution_excel()
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=institution_attendance_report.xlsx"}
    )

@router.get("/report/excel/department/{dept_id}")
async def download_department_report(dept_id: str, current_user: dict = Depends(get_current_user), _=Depends(require_dean)):
    """Download the spreadsheet report representing a specific department."""
    excel_bytes = await ReportService.get_department_excel(dept_id)
    if not excel_bytes:
        raise HTTPException(status_code=404, detail="Department student records not found")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=department_{dept_id}_attendance_report.xlsx"}
    )
