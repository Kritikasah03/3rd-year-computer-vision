"""
object_detection.py
--------------------
Wraps Ultralytics YOLO for object detection.
On the Raspberry Pi, swap "yolov8n.pt" for an even smaller/optimized
export (e.g. an NCNN export) once you get to the optimization phase.
"""

from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # "n" = nano variant - smallest and fastest, best choice for
        # CPU-only hardware like a Raspberry Pi without an accelerator.
        self.model = YOLO(model_path)

    def process(self, frame):
        """
        Run detection on a single frame.
        Returns the raw YOLO result object, which contains boxes,
        class names, and confidence scores.
        """
        # verbose=False stops YOLO from printing logs every frame
        results = self.model(frame, verbose=False)
        return results[0]  # first (and only) image's results

    def to_dict(self, result):
        """
        Convert YOLO's result object into a plain list of dicts -
        this is the format you'll eventually send to Person 3's
        backend over the API, so keep it simple and JSON-friendly.
        """
        detections = []
        for box in result.boxes:
            detections.append({
                "class_name": result.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
            })
        return detections