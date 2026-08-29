from fastapi import (
    APIRouter,
    Query,
    HTTPException
)
from typing import Optional, List

from app.models import (
    SystemStatus,
    DashboardSummary,
    LogResponse,
    LogCreate,
    RobotCommandRequest
)
from app.services.telemetry_service import TelemetryService
from app.services.vision_service import VisionService
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/telemetry", tags=["5G Telemetry & Robot Control"])

telemetry_service = TelemetryService()
vision_service = VisionService()
attendance_service = AttendanceService()


# ============================================================
# 5G & SYSTEM TELEMETRY STATUS
# ============================================================
@router.get("/status", response_model=SystemStatus)
def get_system_telemetry():
    return telemetry_service.get_system_status()


# ============================================================
# DASHBOARD SUMMARY
# ============================================================
@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary():
    enrolled_count = len(vision_service.get_enrolled_persons())
    today_attendance = attendance_service.get_today_count()
    return telemetry_service.get_dashboard_summary(
        total_enrolled=enrolled_count,
        today_attendance=today_attendance
    )


# ============================================================
# SYSTEM EVENT LOGS
# ============================================================
@router.get("/logs", response_model=List[LogResponse])
def get_system_logs(
    limit: int = Query(50, ge=1, le=200, description="Max logs to return")
):
    return telemetry_service.get_logs(limit=limit)


# ============================================================
# CREATE LOG ENTRY
# ============================================================
@router.post("/logs", response_model=LogResponse)
def create_log(log_input: LogCreate):
    return telemetry_service.add_log(log_input.message, log_input.level)


# ============================================================
# DISPATCH ROBOT COMMAND
# ============================================================
@router.post("/robot-command")
def dispatch_robot_command(command_req: RobotCommandRequest):
    telemetry_service.add_log(
        f"Manual robot command dispatched [{command_req.source}]: {command_req.command}",
        "WARNING"
    )
    telemetry_service.current_robot_command = command_req.command
    return {
        "success": True,
        "active_command": command_req.command,
        "source": command_req.source,
        "status": "COMMAND_TRANSMITTED_OVER_5G_EDGE"
    }
