import cv2
import os
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

data_dir = 'enrolled_faces'

faces_data = []
labels = []
label_names = {}
current_label = 0

# Read all enrolled images
for filename in os.listdir(data_dir):
    if filename.endswith('.jpg'):
        # Extract name from filename (e.g., "komal_1.jpg" -> "komal")
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

print(f"Training on {len(faces_data)} images, {len(label_names)} person(s): {label_names}")

# Train the model
recognizer.train(faces_data, np.array(labels))
print("Training complete!")

# Now start live recognition
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

        # Lower confidence = better match in LBPH
        if confidence < 80:
            name = label_names[label]
            text = f"{name} ({round(confidence,1)})"
            color = (0, 255, 0)
        else:
            text = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow('Face Recognition - Press q to quit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()