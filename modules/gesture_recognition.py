"""
gesture_recognition.py
-----------------------
Wraps MediaPipe Hands to detect hand landmarks, then applies a very
simple rule-based check on top to recognize basic gestures.
You can expand the rules or swap in a trained classifier later -
this gives you a working starting point.
"""

import mediapipe as mp


class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

    def process(self, frame):
        rgb_frame = frame[:, :, ::-1]  # BGR -> RGB for MediaPipe
        results = self.hands.process(rgb_frame)
        return results

    def to_dict(self, results):
        """
        Returns a list of detected hands, each with landmarks and
        a simple recognized gesture label.
        """
        hands_data = []
        if not results.multi_hand_landmarks:
            return hands_data

        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
            gesture = self._classify_gesture(hand_landmarks)
            hands_data.append({
                "landmarks": landmarks,
                "gesture": gesture,
            })
        return hands_data

    def _classify_gesture(self, hand_landmarks):
        """
        Very basic example rule: check if all fingertips are above
        (smaller y value than) their corresponding lower knuckles,
        which roughly indicates an "open palm".
        This is intentionally simple - replace/extend with your own
        rules for the specific gestures your project needs
        (e.g. stop, point, wave).
        """
        tips = [8, 12, 16, 20]     # index, middle, ring, pinky fingertip ids
        knuckles = [6, 10, 14, 18]  # corresponding lower knuckle ids

        fingers_up = 0
        for tip_id, knuckle_id in zip(tips, knuckles):
            if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[knuckle_id].y:
                fingers_up += 1

        if fingers_up == 4:
            return "open_palm"
        elif fingers_up == 0:
            return "fist"
        else:
            return "unknown"