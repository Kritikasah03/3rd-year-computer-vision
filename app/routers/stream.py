import cv2
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.unified_engine import UnifiedVisionEngine

router = APIRouter(prefix="/api/stream", tags=["Live Video Streaming"])

unified_engine = UnifiedVisionEngine()


def generate_live_mjpeg_frames(camera_index: int = 0):
    """
    Captures live webcam frames, runs unified AI pipeline with HUD, and yields MJPEG chunks.
    """
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                # If camera is busy or unavailable, yield placeholder frame
                blank_frame = 30 * np.ones((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank_frame, "Camera Stream Idle / Reserved by Client", (80, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                _, buffer = cv2.imencode(".jpg", blank_frame)
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
                time.sleep(0.5)
                continue

            # Process frame with HUD
            annotated_frame = unified_engine.process_frame(
                image=frame,
                mode="all",
                include_annotated_image=False
            )
            
            # Draw HUD
            hud_frame = unified_engine.render_hud(
                frame=frame,
                faces=annotated_frame.get("faces", []),
                gestures=annotated_frame.get("gestures", []),
                objects=annotated_frame.get("objects", []),
                active_command=annotated_frame.get("active_robot_command", "STANDBY")
            )

            _, buffer = cv2.imencode(".jpg", hud_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            frame_bytes = buffer.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            time.sleep(0.03)  # ~30 FPS throttle
    finally:
        cap.release()


@router.get("/mjpeg")
def live_mjpeg_stream():
    """
    Live MJPEG stream with dynamic 5G HUD, multi-person faces, gestures, and objects.
    Directly embeddable in <img> tags in Person 4's dashboard: <img src="http://localhost:8000/api/stream/mjpeg">
    """
    return StreamingResponse(
        generate_live_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
