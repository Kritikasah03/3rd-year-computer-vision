import cv2
import os

# Face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Folder jaha enrolled faces save honge
save_dir = 'enrolled_faces'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Person ka naam pucho
name = input("Enter person's name: ")

cap = cv2.VideoCapture(0)
count = 0

print("Camera khul raha hai... 's' dabao photo capture karne ke liye, 'q' dabao band karne ke liye")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow('Enrollment - Press s to save, q to quit', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            count += 1
            filepath = os.path.join(save_dir, f"{name}_{count}.jpg")
            cv2.imwrite(filepath, face_img)
            print(f"Saved: {filepath}")

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Total {count} images saved for {name}")