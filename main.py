"""
main.py
-------
Combines all four CV modules into one live pipeline.
Run this file to see everything working together on your webcam.
Later, the `output` dict built each frame is what gets sent to
Person 3's backend over the API.
"""

import cv2
import time

from utils.camera import Camera
from modules.object_detection import ObjectDetector
from modules.pose_estimation import PoseEstimator
from modules.gesture_recognition import GestureRecognizer
from modules.scene_segmentation import SceneSegmenter


def main():
    cam = Camera(source=0)

    # Load all four modules once, before the loop starts -
    # loading models is slow, so we never want to do it per-frame.
    detector = ObjectDetector()
    pose_estimator = PoseEstimator()
    gesture_recognizer = GestureRecognizer()
    scene_segmenter = SceneSegmenter()

    prev_time = time.time()

    while True:
        frame = cam.get_frame()
        if frame is None:
            print("Camera returned no frame - stopping.")
            break

        # --- run all modules on this frame ---
        detection_result = detector.process(frame)
        pose_result = pose_estimator.process(frame)
        gesture_result = gesture_recognizer.process(frame)
        segmentation_result = scene_segmenter.process(frame)

        # --- convert results into plain JSON-friendly data ---
        output = {
            "objects": detector.to_dict(detection_result),
            "pose": pose_estimator.to_dict(pose_result),
            "gestures": gesture_recognizer.to_dict(gesture_result),
            # segmentation mask is a numpy array, not JSON-friendly directly -
            # in the real system you'd summarize it or send it separately
        }

        # --- draw detections on the frame just for visual testing ---
        annotated_frame = detection_result.plot()

        # --- FPS counter, useful for judging Pi performance later ---
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Vision Pipeline", annotated_frame)

        # press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()