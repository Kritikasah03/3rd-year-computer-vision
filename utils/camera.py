"""
camera.py
---------
Simple wrapper around OpenCV's VideoCapture.
Every module in this project reads frames through this class,
so if you switch from a laptop webcam to a Pi camera later,
you only change code in ONE place.
"""

import cv2


class Camera:
    def __init__(self, source=0):
        # source=0 means "default webcam". On the Raspberry Pi with a
        # USB camera this is usually still 0. For the Pi Camera Module
        # (CSI ribbon cable) you may instead need a different backend -
        # cross that bridge when you move to the Pi.
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Check the source index/connection.")

    def get_frame(self):
        """Grab one frame from the camera. Returns None if it fails."""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        """Always call this when you're done, to free the camera."""
        self.cap.release()