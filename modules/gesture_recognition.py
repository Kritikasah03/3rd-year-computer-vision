"""
gesture_recognition.py
-----------------------
Wraps MediaPipe Hands to detect hand landmarks, then applies rule-based
logic on top to recognize gestures: open_palm, fist, thumbs_up,
thumbs_down, peace, pointing, or unknown.

Why this version is more robust:
Earlier versions used Y-position (up/down) or X-position (left/right)
comparisons, which only work when the hand happens to be oriented a
certain way. A thumbs-up fist has the thumb pointing straight UP, not
sideways - so an X-based check saw almost no difference and failed.

This version uses DISTANCE instead of direction:
- A finger is "extended" if its tip is farther from a reference point
  than its base knuckle is - regardless of which way it's pointing
  (up, down, sideways, angled). This works no matter how the hand is
  rotated relative to the camera.
- For the 4 fingers (index/middle/ring/pinky): reference point = wrist.
  A curled finger's tip stays close to the wrist; an extended finger's
  tip moves far away, in any direction.
- For the thumb: reference point = index finger's base knuckle (id 5),
  not the wrist. This is because a tucked thumb (fist) lies right
  across the palm near that knuckle regardless of thumb angle, while
  an extended thumb (any direction - up, down, sideways) moves clearly
  away from it.
"""

import math
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

    def _distance(self, a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def _get_finger_states(self, hand_landmarks):
        lm = hand_landmarks.landmark
        wrist = lm[0]
        index_mcp = lm[5]  # reference point for the thumb

        states = {}

        # --- Thumb: distance-from-index-knuckle test (direction-independent) ---
        thumb_tip = lm[4]
        thumb_mcp = lm[2]
        states["thumb"] = self._distance(thumb_tip, index_mcp) > self._distance(thumb_mcp, index_mcp) * 1.3

        # --- Other 4 fingers: distance-from-wrist test ---
        finger_tips = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
        finger_mcps = {"index": 5, "middle": 9, "ring": 13, "pinky": 17}

        for finger in finger_tips:
            tip = lm[finger_tips[finger]]
            mcp = lm[finger_mcps[finger]]
            states[finger] = self._distance(tip, wrist) > self._distance(mcp, wrist) * 1.1

        return states

    def _classify_gesture(self, hand_landmarks):
        lm = hand_landmarks.landmark
        states = self._get_finger_states(hand_landmarks)

        extended = [name for name, is_up in states.items() if is_up]
        num_extended = len(extended)

        # The 4 main fingers, excluding the thumb - the thumb is
        # unreliable to judge when the palm faces the camera flat-on
        # (it tucks close to the hand from that angle even when the
        # gesture is clearly an open palm), so we treat it as optional
        # for this check rather than required.
        four_fingers = ["index", "middle", "ring", "pinky"]
        four_extended = all(states[f] for f in four_fingers)

        # --- Open palm: all 4 main fingers extended (thumb optional) ---
        if four_extended:
            return "open_palm"

        # --- Fist: nothing extended at all ---
        if num_extended == 0:
            return "fist"

        # --- Thumbs up / down: ONLY the thumb is extended ---
        if extended == ["thumb"]:
            wrist_y = lm[0].y
            thumb_tip_y = lm[4].y
            if thumb_tip_y < wrist_y:
                return "thumbs_up"
            else:
                return "thumbs_down"

        # --- Peace sign: only index + middle extended (thumb tucked) ---
        if set(name for name in four_fingers if states[name]) == {"index", "middle"} and not states["thumb"]:
            return "peace"

        # --- Pointing: only index extended (thumb tucked) ---
        if [name for name in four_fingers if states[name]] == ["index"] and not states["thumb"]:
            return "pointing"

        return "unknown"
    