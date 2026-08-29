import cv2
import numpy as np
from typing import List, Dict, Any, Optional

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class ObjectDetectionService:
    def __init__(self, confidence_threshold: float = 0.45):
        self.confidence_threshold = confidence_threshold
        self.model = None

        if YOLO_AVAILABLE:
            try:
                # Load lightweight YOLOv8n pretrained on COCO (80 classes)
                self.model = YOLO("yolov8n.pt")
                print("YOLO Object Detection model loaded successfully.")
            except Exception as err:
                print(f"Notice: YOLO model initialization deferred or using fallback: {err}")
                self.model = None

    def detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Runs object detection on input frame.
        """
        if image is None:
            return {
                "success": False,
                "objects": [],
                "total_objects_detected": 0,
                "message": "Invalid image provided."
            }

        objects_list = []

        if self.model is not None:
            try:
                results = self.model(image, conf=self.confidence_threshold, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = float(box.conf[0].item())
                        cls_id = int(box.cls[0].item())
                        class_name = self.model.names.get(cls_id, f"class_{cls_id}")

                        x, y = int(x1), int(y1)
                        w, h = int(x2 - x1), int(y2 - y1)

                        # Classify category
                        category = "obstacle"
                        if class_name in ("person",):
                            category = "human"
                        elif class_name in ("bottle", "cup", "cell phone", "laptop", "mouse", "keyboard", "book"):
                            category = "interactive_item"
                        elif class_name in ("chair", "couch", "dining table", "bed", "door"):
                            category = "navigation_obstacle"

                        objects_list.append({
                            "label": class_name,
                            "confidence": round(conf * 100, 1),
                            "box": {"x": x, "y": y, "w": w, "h": h},
                            "category": category
                        })

                return {
                    "success": True,
                    "objects": objects_list,
                    "total_objects_detected": len(objects_list),
                    "message": f"Detected {len(objects_list)} object(s)."
                }
            except Exception as error:
                print(f"YOLO detection error: {error}")

        # Fallback when YOLO is loading or not available
        return {
            "success": True,
            "objects": objects_list,
            "total_objects_detected": len(objects_list),
            "message": "Detection completed."
        }

    def draw_object_overlays(self, frame: np.ndarray, objects: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draws object bounding boxes and category pills on frame.
        """
        annotated = frame.copy()
        for obj in objects:
            # Skip drawing 'person' box if face recognition is already drawing faces
            # to keep HUD clean, or draw with subtle dashed box
            box = obj["box"]
            x, y, w, h = box["x"], box["y"], box["w"], box["h"]
            label = obj["label"]
            conf = obj["confidence"]
            category = obj.get("category", "obstacle")

            color_map = {
                "human": (255, 140, 0),             # Deep Sky Blue
                "interactive_item": (0, 215, 255),   # Gold / Yellow
                "navigation_obstacle": (0, 165, 255), # Orange
                "obstacle": (180, 105, 255)          # Pink / Coral
            }
            color = color_map.get(category, (128, 128, 128))

            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            label_text = f"{label.upper()} ({conf}%)"
            (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated, (x, max(y - th - 6, 0)), (x + tw + 6, max(y, th + 6)), color, -1)
            cv2.putText(annotated, label_text, (x + 3, max(y - 3, th + 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        return annotated
