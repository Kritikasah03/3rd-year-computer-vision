import cv2
import numpy as np
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.vision_service import VisionService
from app.services.gesture_service import GestureService
from app.services.object_service import ObjectDetectionService
from app.services.attendance_service import AttendanceService
from app.services.telemetry_service import TelemetryService


class UnifiedVisionEngine:
    def __init__(
        self,
        vision_service: Optional[VisionService] = None,
        gesture_service: Optional[GestureService] = None,
        object_service: Optional[ObjectDetectionService] = None,
        attendance_service: Optional[AttendanceService] = None,
        telemetry_service: Optional[TelemetryService] = None
    ):
        self.attendance_service = attendance_service or AttendanceService()
        self.vision_service = vision_service or VisionService(attendance_service=self.attendance_service)
        self.gesture_service = gesture_service or GestureService()
        self.object_service = object_service or ObjectDetectionService()
        self.telemetry_service = telemetry_service or TelemetryService()

    def process_frame(
        self,
        image: np.ndarray,
        mode: str = "all",
        include_annotated_image: bool = True
    ) -> Dict[str, Any]:
        """
        Executes multi-person face recognition, hand gestures, and object detection.
        Returns combined JSON metadata and optional annotated base64 image.
        """
        start_time = time.time()

        if image is None:
            return {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": 0.0,
                "faces": [],
                "gestures": [],
                "objects": [],
                "total_faces": 0,
                "total_hands": 0,
                "total_objects": 0,
                "active_robot_command": "STANDBY",
                "annotated_image_base64": None,
                "message": "Invalid input image."
            }

        faces_result = {"faces": [], "total_faces_detected": 0}
        gestures_result = {"gestures": [], "total_hands_detected": 0, "active_command": "STANDBY"}
        objects_result = {"objects": [], "total_objects_detected": 0}

        # 1. Multi-Person Face Recognition
        if mode in ("all", "face_only"):
            faces_result = self.vision_service.recognize_faces(image, auto_mark_attendance=True)

        face_boxes = [f["box"] for f in faces_result.get("faces", []) if "box" in f]

        # 2. Hand Gesture Recognition (with face region masked out)
        if mode in ("all", "gesture_only"):
            gestures_result = self.gesture_service.recognize_gestures(image, face_boxes=face_boxes)

        # 3. Object Detection
        if mode in ("all", "object_only"):
            objects_result = self.object_service.detect_objects(image)

        active_command = gestures_result.get("active_command", "STANDBY")

        # 4. Telemetry record
        self.telemetry_service.record_detection_event(
            faces=faces_result.get("faces", []),
            gestures=gestures_result.get("gestures", []),
            objects=objects_result.get("objects", []),
            command=active_command
        )

        # 5. Render HUD Annotation
        annotated_b64 = None
        if include_annotated_image:
            annotated_frame = self.render_hud(
                frame=image,
                faces=faces_result.get("faces", []),
                gestures=gestures_result.get("gestures", []),
                objects=objects_result.get("objects", []),
                active_command=active_command
            )
            # Encode to JPEG
            _, buffer = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            annotated_b64 = base64.b64encode(buffer).decode("utf-8")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": elapsed_ms,
            "faces": faces_result.get("faces", []),
            "gestures": gestures_result.get("gestures", []),
            "objects": objects_result.get("objects", []),
            "total_faces": len(faces_result.get("faces", [])),
            "total_hands": len(gestures_result.get("gestures", [])),
            "total_objects": len(objects_result.get("objects", [])),
            "active_robot_command": active_command,
            "annotated_image_base64": annotated_b64,
            "message": "Frame processed successfully."
        }

    def render_hud(
        self,
        frame: np.ndarray,
        faces: list,
        gestures: list,
        objects: list,
        active_command: str
    ) -> np.ndarray:
        """
        Renders HUD telemetry overlays, face boxes, gesture markers, and object pills.
        """
        h, w = frame.shape[:2]
        hud_frame = frame.copy()

        # Draw objects
        if objects:
            hud_frame = self.object_service.draw_object_overlays(hud_frame, objects)

        # Draw multi-person faces
        if faces:
            hud_frame = self.vision_service.draw_face_overlays(hud_frame, faces)

        # Draw hand gestures
        if gestures:
            hud_frame = self.gesture_service.draw_gesture_overlays(hud_frame, gestures)

        # Draw Top 5G Edge Banner
        banner_h = 32
        overlay = hud_frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.75, hud_frame, 0.25, 0, hud_frame)

        status_text = "5G SA [N78] | LATENCY: 8.4ms | JETSON NANO 10W | EDGE AI"
        cv2.putText(hud_frame, status_text, (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 200), 1)

        # Draw Active Robot Command Banner if active
        if active_command and active_command != "STANDBY":
            cmd_overlay = hud_frame.copy()
            cmd_y = h - 40
            cv2.rectangle(cmd_overlay, (0, cmd_y), (w, h), (0, 0, 180), -1)
            cv2.addWeighted(cmd_overlay, 0.8, hud_frame, 0.2, 0, hud_frame)
            cv2.putText(
                hud_frame,
                f"ROBOT ACTION: {active_command} (TRIGGERED BY GESTURE)",
                (20, h - 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

        return hud_frame
