import cv2
import os
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort

# --- Setup: Face Detection ---
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# --- Setup: Face Recognition (train from enrolled faces) ---
recognizer = cv2.face.LBPHFaceRecognizer_create()
data_dir = 'enrolled_faces'

faces_data = []
labels = []
label_names = {}
current_label = 0

for filename in os.listdir(data_dir):
    if filename.endswith('.jpg'):
        name = filename.rsplit('_', 1)[0]
        if name not in label_names.values():
            label_names[current_label] = name
            person_label = current_label
            current_label += 1
        else:
            person_label = [k for k, v in label_names.items() if v == name][0]

        img_path = os.path.join(data_dir, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (200, 200))
        faces_data.append(img)
        labels.append(person_label)

recognizer.train(faces_data, np.array(labels))
print(f"Training complete! Known people: {label_names}")

# --- Setup: Tracker ---
tracker = DeepSort(max_age=30)

# --- Camera ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Detections for tracker
    detections = []
    for (x, y, w, h) in faces:
        detections.append(([x, y, w, h], 0.9, 'face'))

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)

        # Crop the face region for recognition
        x1c, y1c = max(0, x1), max(0, y1)
        x2c, y2c = min(frame.shape[1], x2), min(frame.shape[0], y2)
        face_roi = gray[y1c:y2c, x1c:x2c]

        name = "Unknown"
        if face_roi.size > 0:
            face_roi_resized = cv2.resize(face_roi, (200, 200))
            label, confidence = recognizer.predict(face_roi_resized)
            if confidence < 80:
                name = label_names[label]

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        display_text = f"{name} | ID:{track_id}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, display_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Tracking + Recognition - Press q to quit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()