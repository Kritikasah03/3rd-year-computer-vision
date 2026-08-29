from fastapi import (
    APIRouter,
    Query,
    HTTPException,
    Response
)
from typing import Optional

from app.models import (
    AttendanceListResponse,
    AttendanceMarkRequest
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/attendance", tags=["Attendance Management"])
attendance_service = AttendanceService()


# ============================================================
# GET ATTENDANCE RECORDS
# ============================================================
@router.get("", response_model=AttendanceListResponse)
def get_attendance(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, or 'all'"),
    search: Optional[str] = Query(None, description="Search by person name")
):
    records = attendance_service.get_attendance(date_filter=date, name_filter=search)
    return {
        "success": True,
        "total_records": len(records),
        "records": records
    }


# ============================================================
# GET TODAY'S ATTENDANCE
# ============================================================
@router.get("/today", response_model=AttendanceListResponse)
def get_today_attendance():
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    records = attendance_service.get_attendance(date_filter=today_str)
    return {
        "success": True,
        "total_records": len(records),
        "records": records
    }


# ============================================================
# MARK ATTENDANCE MANUALLY
# ============================================================
@router.post("/mark")
def mark_attendance(request: AttendanceMarkRequest):
    result = attendance_service.mark_attendance_manual(
        person_name=request.name,
        date_str=request.date,
        time_str=request.time
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to mark attendance"))
    return result


# ============================================================
# CLEAR ATTENDANCE RECORDS
# ============================================================
@router.delete("/clear")
def clear_attendance():
    return attendance_service.clear_attendance()


# ============================================================
# EXPORT ATTENDANCE AS CSV
# ============================================================
@router.get("/export")
def export_attendance_csv():
    records = attendance_service.get_attendance(date_filter="all")
    csv_content = "ID,Name,Date,Time\n"
    for r in records:
        csv_content += f"{r['id']},{r['name']},{r['date']},{r['time']}\n"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_export.csv"}
    )
