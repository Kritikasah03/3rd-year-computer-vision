"""
object_detection.py
--------------------
Wraps Ultralytics YOLO for object detection.

Two important filters are applied here:
1. exclude_classes - drops classes that belong to someone else's module
   (e.g. "person" is Person 1's job - face recognition/tracking - so we
   don't want our object detector drawing boxes on people at all).
2. confidence_threshold - drops low-confidence, likely-wrong guesses
   (e.g. "cat 0.32" - only 32% sure - should never be shown).
"""

from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5, exclude_classes=None):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        # Default: exclude "person" since that's Person 1's responsibility
        self.exclude_classes = exclude_classes if exclude_classes is not None else ["person"]

    def process(self, frame):
        """Run YOLO on a frame and return the raw result object."""
        results = self.model(frame, verbose=False)
        return results[0]

    def to_dict(self, result):
        """
        Convert YOLO's result into a filtered, JSON-friendly list.
        Only keeps detections that are:
        - not in exclude_classes
        - above the confidence_threshold
        """
        detections = []
        for box in result.boxes:
            class_name = result.names[int(box.cls[0])]
            confidence = float(box.conf[0])

            if class_name in self.exclude_classes:
                continue
            if confidence < self.confidence_threshold:
                continue

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "bbox": box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
            })
        return detections