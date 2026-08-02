"""
main.py
-------
Combines all four CV modules into one live pipeline.

Smoothing added: raw gesture detection can flicker frame-to-frame due
to small hand tremor/noise. We buffer the last few readings per hand
and only display the MOST COMMON one in that window, so the label
stays stable instead of jumping around every frame.
"""

import cv2
import time
from collections import deque, Counter

from utils.camera import Camera
from modules.object_detection import ObjectDetector
from modules.pose_estimation import PoseEstimator
from modules.gesture_recognition import GestureRecognizer
from modules.scene_segmentation import SceneSegmenter

SMOOTHING_WINDOW = 5  # number of recent frames to vote across


def draw_object_detections(frame, detections):
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        label = f'{det["class_name"]} {det["confidence"]:.2f}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, label, (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    return frame


def draw_status_text(frame, pose_landmarks, smoothed_gestures):
    y_offset = 70

    if pose_landmarks:
        cv2.putText(frame, "Pose: detected", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        y_offset += 35

    for i, gesture in enumerate(smoothed_gestures):
        cv2.putText(frame, f"Hand {i+1}: {gesture}", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        y_offset += 35

    return frame


def smooth_gestures(gesture_list, history_buffers):
    """
    Keeps a rolling window of the last N gesture readings for each
    hand slot, and returns the most frequent (majority-vote) label
    per hand - this is what actually stops the flicker.
    """
    smoothed = []
    for i, hand in enumerate(gesture_list):
        if i not in history_buffers:
            history_buffers[i] = deque(maxlen=SMOOTHING_WINDOW)
        history_buffers[i].append(hand["gesture"])

        most_common = Counter(history_buffers[i]).most_common(1)[0][0]
        smoothed.append(most_common)

    # clear buffers for hand slots that disappeared this frame
    for i in list(history_buffers.keys()):
        if i >= len(gesture_list):
            del history_buffers[i]

    return smoothed


def main():
    cam = Camera(source=0)

    detector = ObjectDetector(confidence_threshold=0.5, exclude_classes=["person"])
    pose_estimator = PoseEstimator()
    gesture_recognizer = GestureRecognizer()
    scene_segmenter = SceneSegmenter()

    gesture_history = {}  # hand index -> deque of recent gesture labels
    prev_time = time.time()

    while True:
        frame = cam.get_frame()
        if frame is None:
            print("Camera returned no frame - stopping.")
            break

        detection_result = detector.process(frame)
        pose_result = pose_estimator.process(frame)
        gesture_result = gesture_recognizer.process(frame)
        segmentation_result = scene_segmenter.process(frame)

        object_detections = detector.to_dict(detection_result)
        gesture_list = gesture_recognizer.to_dict(gesture_result)
        smoothed_gestures = smooth_gestures(gesture_list, gesture_history)

        output = {
            "objects": object_detections,
            "pose": pose_estimator.to_dict(pose_result),
            "gestures": gesture_list,          # raw, unsmoothed - use for backend hand-off
            "gestures_smoothed": smoothed_gestures,  # stable labels - use for display/decisions
        }

        annotated_frame = frame.copy()
        annotated_frame = draw_object_detections(annotated_frame, object_detections)
        annotated_frame = draw_status_text(annotated_frame, pose_result.pose_landmarks, smoothed_gestures)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Vision Pipeline", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()