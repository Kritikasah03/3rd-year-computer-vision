import cv2
import numpy as np
import math
from collections import deque
from typing import List, Dict, Any, Optional, Tuple

class GestureService:
    ROBOT_COMMAND_MAP = {
        "THUMBS_UP": "FOLLOW_ME",
        "THUMBS_DOWN": "RETREAT",
        "FIST": "EMERGENCY_STOP",
        "OPEN_PALM": "WAIT_HOLD",
        "POINTING": "NAVIGATE_TARGET",
        "PEACE": "GREET_STANDBY",
        "UNKNOWN": "STANDBY"
    }

    def __init__(self, buffer_size: int = 4):
        self.mp_hands = None
        self.mp_detector = None
        self.gesture_history = deque(maxlen=buffer_size)
        self.last_confirmed_command = "STANDBY"
        self._init_mediapipe()

    def _init_mediapipe(self):
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self.mp_hands = mp.solutions.hands
                self.mp_detector = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.6
                )
                print("MediaPipe Hands Solutions initialized.")
            else:
                print("MediaPipe active; enhanced hybrid hand analyzer ready.")
        except Exception as err:
            print(f"MediaPipe init notice: {err}.")

    def _classify_contour_gesture(self, contour, frame_w: int, frame_h: int) -> Tuple[str, float, Dict[str, int]]:
        x, y, w, h = cv2.boundingRect(contour)
        box = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}

        # Hand must be reasonably sized and shaped
        if w < 50 or h < 50 or w * h < 4000:
            return "UNKNOWN", 0.0, box

        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is None or len(hull) < 4:
            return "UNKNOWN", 0.0, box

        try:
            defects = cv2.convexityDefects(contour, hull)
        except Exception:
            defects = None

        defect_count = 0
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])

                a = math.hypot(end[0] - start[0], end[1] - start[1])
                b = math.hypot(far[0] - start[0], far[1] - start[1])
                c = math.hypot(end[0] - far[0], end[1] - far[1])

                if b * c > 0:
                    angle = math.degrees(math.acos(max(-1.0, min(1.0, (b**2 + c**2 - a**2) / (2 * b * c)))))
                    if angle <= 80 and d > 4000:  # Strict finger separation
                        defect_count += 1

        aspect_ratio = float(w) / h
        area = cv2.contourArea(contour)
        hull_area = cv2.contourArea(cv2.convexHull(contour, returnPoints=True))
        solidity = float(area) / hull_area if hull_area > 0 else 0

        # High-confidence gesture classification
        if defect_count == 1:
            # Peace sign (V shape)
            if 0.4 < aspect_ratio < 1.1:
                return "PEACE", 0.92, box

        elif defect_count >= 3:
            # Open palm with spread fingers
            if 0.6 < aspect_ratio < 1.4 and solidity < 0.78:
                return "OPEN_PALM", 0.94, box

        elif defect_count == 0:
            if aspect_ratio < 0.55 and solidity < 0.85:
                # Vertical pointing finger
                return "POINTING", 0.90, box
            elif aspect_ratio > 1.35 and solidity > 0.70:
                # Extended thumb
                return "THUMBS_UP", 0.88, box

        return "UNKNOWN", 0.0, box

    def recognize_gestures(self, image: np.ndarray, face_boxes: Optional[List[Dict[str, int]]] = None) -> Dict[str, Any]:
        if image is None:
            return {
                "success": False,
                "gestures": [],
                "total_hands_detected": 0,
                "active_command": "STANDBY",
                "message": "Invalid image."
            }

        img_h, img_w = image.shape[:2]
        gestures_list = []
        raw_gesture = "UNKNOWN"
        active_command = "STANDBY"

        # 1. MediaPipe Solution
        if self.mp_detector is not None:
            try:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.mp_detector.process(rgb_image)
                if results.multi_hand_landmarks and results.multi_handedness:
                    for hand_landmarks, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                        hand_label = handedness_info.classification[0].label
                        landmarks = hand_landmarks.landmark
                        wrist = landmarks[0]
                        thumb_tip = landmarks[4]
                        index_tip = landmarks[8]
                        middle_tip = landmarks[12]
                        ring_tip = landmarks[16]
                        pinky_tip = landmarks[20]

                        index_ext = index_tip.y < landmarks[6].y
                        middle_ext = middle_tip.y < landmarks[10].y
                        ring_ext = ring_tip.y < landmarks[14].y
                        pinky_ext = pinky_tip.y < landmarks[18].y
                        thumb_up = (thumb_tip.y < landmarks[2].y) and (thumb_tip.y < landmarks[5].y)
                        thumb_down = (thumb_tip.y > landmarks[2].y) and (thumb_tip.y > wrist.y)

                        num_ext = sum([index_ext, middle_ext, ring_ext, pinky_ext])

                        gesture = "UNKNOWN"
                        conf = 70.0
                        if num_ext == 0 and thumb_up:
                            gesture = "THUMBS_UP"
                            conf = 96.0
                        elif num_ext == 0 and thumb_down:
                            gesture = "THUMBS_DOWN"
                            conf = 95.0
                        elif num_ext == 0 and not thumb_up and not thumb_down:
                            gesture = "FIST"
                            conf = 92.0
                        elif num_ext == 4:
                            gesture = "OPEN_PALM"
                            conf = 96.0
                        elif index_ext and not middle_ext and not ring_ext and not pinky_ext:
                            gesture = "POINTING"
                            conf = 94.0
                        elif index_ext and middle_ext and not ring_ext and not pinky_ext:
                            gesture = "PEACE"
                            conf = 95.0

                        if gesture != "UNKNOWN":
                            raw_gesture = gesture

                        x_coords = [int(lm.x * img_w) for lm in landmarks]
                        y_coords = [int(lm.y * img_h) for lm in landmarks]
                        box = {
                            "x": max(0, min(x_coords) - 15),
                            "y": max(0, min(y_coords) - 15),
                            "w": min(img_w, max(x_coords) + 15) - max(0, min(x_coords) - 15),
                            "h": min(img_h, max(y_coords) + 15) - max(0, min(y_coords) - 15)
                        }

                        robot_action = self.ROBOT_COMMAND_MAP.get(gesture, "STANDBY")

                        gestures_list.append({
                            "hand": hand_label,
                            "gesture": gesture,
                            "confidence": conf,
                            "robot_action": robot_action,
                            "box": box
                        })

                    # Filter with temporal smoothing
                    self.gesture_history.append(raw_gesture)
                    if len(self.gesture_history) >= 2 and all(g == raw_gesture for g in list(self.gesture_history)[-2:]):
                        active_command = self.ROBOT_COMMAND_MAP.get(raw_gesture, "STANDBY")
                    else:
                        active_command = "STANDBY"

                    return {
                        "success": True,
                        "gestures": gestures_list,
                        "total_hands_detected": len(gestures_list),
                        "active_command": active_command,
                        "message": f"Detected {len(gestures_list)} hand(s)."
                    }
            except Exception as mp_err:
                print(f"MediaPipe processing error: {mp_err}")

        # 2. Enhanced Skin Mask Hand Segmentation (with Face Exclusion)
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 30, 60], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # Mask out face bounding boxes to avoid face/ear/neck false positives
            if face_boxes:
                for fb in face_boxes:
                    fx, fy, fw, fh = fb.get("x", 0), fb.get("y", 0), fb.get("w", 0), fb.get("h", 0)
                    cv2.rectangle(mask, (max(0, fx - 20), max(0, fy - 20)), (min(img_w, fx + fw + 20), min(img_h, fy + fh + int(fh * 0.4))), 0, -1)

            # Morphological cleanup
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.dilate(mask, kernel, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_contours = [c for c in contours if cv2.contourArea(c) > 4500]
            sorted_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)[:2]

            for idx, c in enumerate(sorted_contours):
                gesture, conf, box = self._classify_contour_gesture(c, img_w, img_h)
                if gesture != "UNKNOWN":
                    hand_name = "Right" if idx == 0 else "Left"
                    robot_action = self.ROBOT_COMMAND_MAP.get(gesture, "STANDBY")
                    raw_gesture = gesture
                    gestures_list.append({
                        "hand": hand_name,
                        "gesture": gesture,
                        "confidence": round(conf * 100, 1),
                        "robot_action": robot_action,
                        "box": box
                    })
        except Exception as contour_err:
            print(f"Contour gesture detection error: {contour_err}")

        # Temporal smoothing filter
        self.gesture_history.append(raw_gesture)
        if len(self.gesture_history) >= 2 and all(g == raw_gesture for g in list(self.gesture_history)[-2:]):
            active_command = self.ROBOT_COMMAND_MAP.get(raw_gesture, "STANDBY")
        else:
            active_command = "STANDBY"

        return {
            "success": True,
            "gestures": gestures_list,
            "total_hands_detected": len(gestures_list),
            "active_command": active_command,
            "message": f"Processed {len(gestures_list)} gesture(s)."
        }

    def draw_gesture_overlays(self, frame: np.ndarray, gestures: List[Dict[str, Any]]) -> np.ndarray:
        annotated = frame.copy()
        for g in gestures:
            box = g.get("box")
            if not box:
                continue

            x, y, w, h = box["x"], box["y"], box["w"], box["h"]
            gesture_name = g["gesture"]
            if gesture_name == "UNKNOWN":
                continue

            robot_action = g["robot_action"]
            hand = g["hand"]
            conf = g["confidence"]

            color_map = {
                "THUMBS_UP": (0, 255, 128),
                "THUMBS_DOWN": (0, 140, 255),
                "FIST": (0, 0, 255),
                "OPEN_PALM": (255, 200, 0),
                "POINTING": (255, 0, 255),
                "PEACE": (255, 255, 0)
            }
            color = color_map.get(gesture_name, (200, 200, 200))

            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            cv2.circle(annotated, (x, y), 5, color, -1)
            cv2.circle(annotated, (x + w, y + h), 5, color, -1)

            label_text = f"{hand.upper()} HAND: {gesture_name} [{conf}%]"
            cmd_text = f"CMD: {robot_action}"

            (tw1, th1), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            (tw2, th2), _ = cv2.getTextSize(cmd_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            max_w = max(tw1, tw2)

            badge_y = max(y - 10, th1 + th2 + 20)
            cv2.rectangle(annotated, (x, badge_y - th1 - th2 - 14), (x + max_w + 14, badge_y + 4), color, -1)
            cv2.putText(annotated, label_text, (x + 7, badge_y - th2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(annotated, cmd_text, (x + 7, badge_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return annotated
