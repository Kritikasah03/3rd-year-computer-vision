from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Query,
    HTTPException,
    Depends
)
import cv2
import numpy as np
from typing import Optional

from app.models import (
    UnifiedVisionProcessResponse,
    MultiFaceRecognitionResponse,
    GestureRecognitionResponse,
    ObjectDetectionResponse
)
from app.services.unified_engine import UnifiedVisionEngine
from app.services.vision_service import VisionService
from app.services.gesture_service import GestureService
from app.services.object_service import ObjectDetectionService

router = APIRouter(prefix="/api/vision", tags=["Vision Intelligence"])

# Shared service instances
vision_service = VisionService()
gesture_service = GestureService()
object_service = ObjectDetectionService()
unified_engine = UnifiedVisionEngine(
    vision_service=vision_service,
    gesture_service=gesture_service,
    object_service=object_service
)


async def decode_upload_image(image: UploadFile) -> np.ndarray:
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image.")

    contents = await image.read()
    image_array = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image data.")

    return frame


# ============================================================
# UNIFIED VISION PROCESSING (FACES + GESTURES + OBJECTS)
# ============================================================
@router.post("/process", response_model=UnifiedVisionProcessResponse)
async def process_frame(
    image: UploadFile = File(...),
    mode: str = Query("all", description="Mode: 'all', 'face_only', 'gesture_only', 'object_only'"),
    include_annotated_image: bool = Query(True, description="Include base64 annotated frame in response")
):
    try:
        frame = await decode_upload_image(image)
        result = unified_engine.process_frame(
            image=frame,
            mode=mode,
            include_annotated_image=include_annotated_image
        )
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# MULTI-PERSON FACE RECOGNITION
# ============================================================
@router.post("/recognize-faces", response_model=MultiFaceRecognitionResponse)
async def recognize_multiple_faces(
    image: UploadFile = File(...),
    auto_attendance: bool = Query(True, description="Automatically mark attendance for recognized individuals")
):
    try:
        frame = await decode_upload_image(image)
        result = vision_service.recognize_faces(frame, auto_mark_attendance=auto_attendance)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# HAND GESTURE RECOGNITION
# ============================================================
@router.post("/gestures", response_model=GestureRecognitionResponse)
async def recognize_gestures(
    image: UploadFile = File(...)
):
    try:
        frame = await decode_upload_image(image)
        result = gesture_service.recognize_gestures(frame)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# OBJECT DETECTION
# ============================================================
@router.post("/objects", response_model=ObjectDetectionResponse)
async def detect_objects(
    image: UploadFile = File(...)
):
    try:
        frame = await decode_upload_image(image)
        result = object_service.detect_objects(frame)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# ENROLL FACE
# ============================================================
@router.post("/enroll")
async def enroll_face(
    name: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        frame = await decode_upload_image(image)
        result = vision_service.enroll_face(name, frame)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# TRAIN MODEL
# ============================================================
@router.post("/train")
def train_model():
    try:
        return vision_service.train_model()
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# GET ENROLLED PERSONS
# ============================================================
@router.get("/enrolled-persons")
def get_enrolled_persons():
    persons = vision_service.get_enrolled_persons()
    return {
        "success": True,
        "persons": persons,
        "total_persons": len(persons)
    }


# ============================================================
# DELETE ENROLLED PERSON
# ============================================================
@router.delete("/enrolled-persons/{person_name}")
def delete_enrolled_person(person_name: str):
    return vision_service.delete_enrolled_person(person_name)
