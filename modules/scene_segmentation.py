"""
scene_segmentation.py
----------------------
Lightweight segmentation using MediaPipe's Selfie Segmentation model.
NOTE: this segments "person vs background" only - it's a scoped-down
starting point that's realistic to run on a Raspberry Pi CPU.
Full multi-class scene segmentation (walls, floor, furniture, etc.)
needs a much heavier model - discuss with your team whether that
level of detail is actually required, given Pi hardware limits.
"""

import mediapipe as mp
import numpy as np


class SceneSegmenter:
    def __init__(self):
        self.mp_selfie = mp.solutions.selfie_segmentation
        self.segmenter = self.mp_selfie.SelfieSegmentation(model_selection=1)
        # model_selection=1 -> "landscape" model, faster, good for real-time

    def process(self, frame):
        rgb_frame = frame[:, :, ::-1]  # BGR -> RGB for MediaPipe
        results = self.segmenter.process(rgb_frame)
        return results

    def get_mask(self, results, threshold=0.5):
        """
        Returns a binary mask (numpy array) where True = person/foreground,
        False = background. Useful for the navigation module to know
        which parts of the frame are "walkable" background vs a person
        or obstacle in front of the camera.
        """
        condition = results.segmentation_mask > threshold
        return condition.astype(np.uint8)  # 0s and 1s, easy to send onward