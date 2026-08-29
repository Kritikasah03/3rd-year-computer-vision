import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models import (
    SystemStatus,
    DashboardSummary,
    NetworkTelemetry,
    EdgeDeviceTelemetry,
    LogResponse
)


class TelemetryService:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = [
            {
                "id": 1,
                "message": "Vision Intelligence Backend initialized for Autonomous Humanoid Robot.",
                "level": "INFO",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": 2,
                "message": "Private 5G SA Link established on Band N78. Edge AI telemetry online.",
                "level": "INFO",
                "timestamp": datetime.now().isoformat()
            }
        ]
        self.log_counter = 3
        self.total_detections = 0
        self.recognized_faces_count = 0
        self.current_robot_command = "STANDBY"
        self.active_gestures_count = 0
        self.latest_faces_count = 0
        self.latest_objects_count = 0

    def add_log(self, message: str, level: str = "INFO") -> Dict[str, Any]:
        log_entry = {
            "id": self.log_counter,
            "message": message,
            "level": level.upper(),
            "timestamp": datetime.now().isoformat()
        }
        self.logs.append(log_entry)
        self.log_counter += 1
        # Keep latest 200 logs
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]
        return log_entry

    def record_detection_event(self, faces: list, gestures: list, objects: list, command: str):
        num_faces = len(faces)
        num_gestures = len(gestures)
        num_objects = len(objects)

        self.latest_faces_count = num_faces
        self.active_gestures_count = num_gestures
        self.latest_objects_count = num_objects
        self.total_detections += (num_faces + num_gestures + num_objects)

        for f in faces:
            if f.get("is_recognized"):
                self.recognized_faces_count += 1
                if f.get("attendance_marked"):
                    self.add_log(f"Auto attendance recorded for: {f['name']}", "SUCCESS")

        if command and command != "STANDBY":
            if command != self.current_robot_command:
                self.add_log(f"Humanoid Robot Command Activated via Gesture: {command}", "WARNING")
            self.current_robot_command = command

    def get_system_status(self) -> SystemStatus:
        # Dynamic 5G edge telemetry simulation (realistic low-latency values)
        simulated_latency = round(random.uniform(7.8, 10.5), 1)
        simulated_jitter = round(random.uniform(0.8, 1.8), 1)
        simulated_bw = round(random.uniform(365.0, 420.0), 1)

        simulated_cpu = round(random.uniform(28.0, 42.0), 1)
        simulated_gpu = round(random.uniform(40.0, 65.0), 1)
        simulated_temp = round(random.uniform(44.0, 49.5), 1)

        net_telemetry = NetworkTelemetry(
            network_type="Private 5G SA (Standalone)",
            band="N78 (3.5 GHz - Ultra Low Latency)",
            latency_ms=simulated_latency,
            jitter_ms=simulated_jitter,
            bandwidth_mbps=simulated_bw,
            signal_rsrp_dbm=-75,
            status="OPTIMAL"
        )

        edge_telemetry = EdgeDeviceTelemetry(
            device_model="NVIDIA Jetson Nano / Edge AI Server",
            cpu_usage_pct=simulated_cpu,
            gpu_usage_pct=simulated_gpu,
            memory_used_mb=1920,
            memory_total_mb=4096,
            temperature_c=simulated_temp,
            power_mode="10W MAXN"
        )

        return SystemStatus(
            system_status="OPERATIONAL",
            camera_status="ONLINE",
            ai_status="READY",
            network_status="CONNECTED",
            network_telemetry=net_telemetry,
            edge_telemetry=edge_telemetry
        )

    def get_dashboard_summary(self, total_enrolled: int = 0, today_attendance: int = 0) -> DashboardSummary:
        return DashboardSummary(
            system_status="OPERATIONAL",
            camera_status="ONLINE",
            ai_status="READY",
            total_detections=self.total_detections,
            recognized_faces=self.recognized_faces_count,
            total_enrolled_persons=total_enrolled,
            today_attendance_count=today_attendance,
            active_gestures_count=self.active_gestures_count,
            current_robot_command=self.current_robot_command,
            edge_latency_ms=round(random.uniform(7.8, 10.2), 1),
            total_logs=len(self.logs)
        )

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self.logs[-limit:]))
