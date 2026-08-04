import cv2
import os
import numpy as np
import csv
from datetime import datetime

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

data_dir = 'enrolled_faces'
attendance_file = 'attendance.csv'

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
print("Training complete!")

if not os.path.exists(attendance_file):
    with open(attendance_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Date', 'Time'])

marked_today = set()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (200, 200))
        label, confidence = recognizer.predict(face_roi)

        if confidence < 60:
            name = label_names[label]
            color = (0, 255, 0)
            display_text = f"{name} ({round(100-confidence, 1)}%)"

            if name not in marked_today:
                now = datetime.now()
                with open(attendance_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')])
                marked_today.add(name)
                print(f"Attendance marked for {name}")
        else:
            display_text = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, display_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow('Attendance System - Press q to quit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Attendance saved to attendance.csv")