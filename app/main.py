import cv2
import numpy as np
from pathlib import Path
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.services.vision_service import VisionService
from app.routers import vision, attendance, telemetry, stream

# ============================================================
# FASTAPI APPLICATION SETUP
# ============================================================

app = FastAPI(
    title="Private 5G Vision Intelligence System",
    description=(
        "Unified Edge AI Vision Backend for Autonomous Humanoid Robots.\n"
        "Featuring Multi-Person Face Recognition, MediaPipe Hand Gesture Control, "
        "YOLO Object Detection, Automated Attendance Logging, and 5G Telemetry."
    ),
    version="2.0.0"
)

# Enable CORS for Person 4's frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# PATHS & STATIC FILES
# ============================================================

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ============================================================
# ROUTERS INCLUSION
# ============================================================

app.include_router(vision.router)
app.include_router(attendance.router)
app.include_router(telemetry.router)
app.include_router(stream.router)

# Shared vision service instance for legacy direct endpoints
legacy_vision_service = VisionService()


# ============================================================
# CORE / SYSTEM ENDPOINTS
# ============================================================

@app.get("/")
def home():
    return {
        "system": "Private 5G Vision Intelligence System for Autonomous Humanoid Robots",
        "status": "ONLINE",
        "version": "2.0.0",
        "capabilities": [
            "Simultaneous Multi-Person Face Recognition",
            "MediaPipe Hand Gesture Control (Thumbs Up/Down, Fist, Open Palm, Pointing, Peace)",
            "YOLO Object & Obstacle Detection",
            "Automated Debounced Attendance Logging",
            "Live MJPEG Stream (/api/stream/mjpeg)",
            "5G Edge Network Telemetry (/api/telemetry/status)"
        ],
        "endpoints": {
            "webcam_tester": "/webcam",
            "swagger_docs": "/docs",
            "redoc": "/redoc",
            "attendance": "/api/attendance",
            "telemetry_summary": "/api/telemetry/summary",
            "live_stream": "/api/stream/mjpeg"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system_status": "OPERATIONAL",
        "5g_network": "CONNECTED",
        "ai_engine": "ACTIVE"
    }


@app.get("/webcam", response_class=HTMLResponse)
def webcam_page():
    webcam_file = STATIC_DIR / "webcam.html"
    if not webcam_file.exists():
        raise HTTPException(
            status_code=404,
            detail="webcam.html not found in app/static/"
        )
    return webcam_file.read_text(encoding="utf-8")


# ============================================================
# BACKWARD COMPATIBILITY ENDPOINTS (PRESERVING PERSON 1 & 3 CALLS)
# ============================================================

@app.post("/enroll")
async def enroll_face_legacy(
    name: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Please upload a valid image.")

        contents = await image.read()
        image_array = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data.")

        return legacy_vision_service.enroll_face(name, frame)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/train")
def train_model_legacy():
    return legacy_vision_service.train_model()


@app.post("/recognize")
async def recognize_face_legacy(
    image: UploadFile = File(...)
):
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Please upload a valid image.")

        contents = await image.read()
        image_array = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data.")

        # Returns multi-face results with top face for backward compatibility
        return legacy_vision_service.recognize_face(frame)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/enrolled-persons")
def enrolled_persons_legacy():
    persons = legacy_vision_service.get_enrolled_persons()
    return {
        "success": True,
        "persons": persons,
        "total_persons": len(persons)
    }