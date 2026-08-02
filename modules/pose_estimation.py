"""
pose_estimation.py
-------------------
Wraps MediaPipe Pose for human pose (skeleton keypoint) estimation.
MediaPipe is CPU-friendly, which makes it a better default than a
heavy deep-learning pose model when running on a Raspberry Pi.
"""

import mediapipe as mp


class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        # static_image_mode=False -> optimized for continuous video,
        # not single unrelated photos
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,   # 0 = fastest/least accurate, 2 = slowest/most accurate
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame):
        """
        Run pose estimation on a frame.
        MediaPipe expects RGB images, but OpenCV gives us BGR by
        default - so we convert before processing.
        """
        rgb_frame = frame[:, :, ::-1]  # quick BGR -> RGB flip
        results = self.pose.process(rgb_frame)
        return results

    def to_dict(self, results):
        """
        Convert MediaPipe's landmark output into a plain list of
        dicts (JSON-friendly), one entry per body keypoint.
        """
        if not results.pose_landmarks:
            return []

        keypoints = []
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            keypoints.append({
                "id": idx,
                "x": landmark.x,       # normalized 0-1 (relative to frame width)
                "y": landmark.y,       # normalized 0-1 (relative to frame height)
                "visibility": landmark.visibility,
            })
        return keypoints