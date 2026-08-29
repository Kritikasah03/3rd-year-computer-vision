from datetime import datetime


logs = [
    {
        "id": 1,
        "message": "Vision Intelligence Backend started successfully",
        "level": "INFO",
        "timestamp": datetime.now().isoformat()
    }
]


detections = [
    {
        "id": 1,
        "object_name": "Person",
        "confidence": 0.95,
        "camera_id": "CAM-01",
        "timestamp": datetime.now().isoformat()
    }
]


faces = [
    {
        "id": 1,
        "name": "Unknown",
        "confidence": 0.0,
        "camera_id": "CAM-01",
        "timestamp": datetime.now().isoformat()
    }
]