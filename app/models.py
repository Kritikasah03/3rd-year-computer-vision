from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int


class FaceRecognitionResult(BaseModel):
    name: str
    confidence: float
    distance: float
    box: BoundingBox
    is_recognized: bool
    attendance_marked: bool = False


class MultiFaceRecognitionResponse(BaseModel):
    success: bool
    faces: List[FaceRecognitionResult] = []
    total_faces_detected: int = 0
    recognized_count: int = 0
    unknown_count: int = 0
    message: Optional[str] = None


class GestureDetectionResult(BaseModel):
    hand: str  # "Left" or "Right"
    gesture: str  # "THUMBS_UP", "THUMBS_DOWN", "FIST", "OPEN_PALM", "POINTING", "PEACE", "UNKNOWN"
    confidence: float
    robot_action: str  # e.g., "FOLLOW_ME", "EMERGENCY_STOP", "WAIT", "NAVIGATE", "GREET"
    box: Optional[BoundingBox] = None


class GestureRecognitionResponse(BaseModel):
    success: bool
    gestures: List[GestureDetectionResult] = []
    total_hands_detected: int = 0
    active_command: Optional[str] = "STANDBY"
    message: Optional[str] = None


class ObjectDetectionResult(BaseModel):
    label: str
    confidence: float
    box: BoundingBox
    category: str = "general"


class ObjectDetectionResponse(BaseModel):
    success: bool
    objects: List[ObjectDetectionResult] = []
    total_objects_detected: int = 0
    message: Optional[str] = None


class UnifiedVisionProcessResponse(BaseModel):
    success: bool
    timestamp: str
    execution_time_ms: float
    faces: List[FaceRecognitionResult] = []
    gestures: List[GestureDetectionResult] = []
    objects: List[ObjectDetectionResult] = []
    total_faces: int = 0
    total_hands: int = 0
    total_objects: int = 0
    active_robot_command: str = "STANDBY"
    annotated_image_base64: Optional[str] = None
    message: Optional[str] = None


class AttendanceRecord(BaseModel):
    id: int
    name: str
    date: str
    time: str


class AttendanceListResponse(BaseModel):
    success: bool
    total_records: int
    records: List[AttendanceRecord] = []


class AttendanceMarkRequest(BaseModel):
    name: str
    date: Optional[str] = None
    time: Optional[str] = None


class NetworkTelemetry(BaseModel):
    network_type: str = "Private 5G SA (Standalone)"
    band: str = "N78 (3.5 GHz)"
    latency_ms: float = 8.4
    jitter_ms: float = 1.2
    bandwidth_mbps: float = 380.0
    signal_rsrp_dbm: int = -76
    status: str = "OPTIMAL"


class EdgeDeviceTelemetry(BaseModel):
    device_model: str = "NVIDIA Jetson Nano / Edge AI"
    cpu_usage_pct: float = 34.5
    gpu_usage_pct: float = 48.0
    memory_used_mb: int = 1840
    memory_total_mb: int = 4096
    temperature_c: float = 46.2
    power_mode: str = "10W MAXN"


class SystemStatus(BaseModel):
    system_status: str = "OPERATIONAL"
    camera_status: str = "ONLINE"
    ai_status: str = "READY"
    network_status: str = "CONNECTED"
    network_telemetry: NetworkTelemetry = Field(default_factory=NetworkTelemetry)
    edge_telemetry: EdgeDeviceTelemetry = Field(default_factory=EdgeDeviceTelemetry)


class DashboardSummary(BaseModel):
    system_status: str = "OPERATIONAL"
    camera_status: str = "ONLINE"
    ai_status: str = "READY"
    total_detections: int = 0
    recognized_faces: int = 0
    total_enrolled_persons: int = 0
    today_attendance_count: int = 0
    active_gestures_count: int = 0
    current_robot_command: str = "STANDBY"
    edge_latency_ms: float = 8.4
    total_logs: int = 0


class LogCreate(BaseModel):
    message: str
    level: str = "INFO"


class LogResponse(BaseModel):
    id: int
    message: str
    level: str
    timestamp: str


class RobotCommandRequest(BaseModel):
    command: str
    source: str = "MANUAL_OVERRIDE"
    parameters: Optional[Dict[str, Any]] = None