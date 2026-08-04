import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Tracker initialize karo
tracker = DeepSort(max_age=30)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # DeepSORT ko detections ka format chahiye: [[x, y, w, h], confidence, class]
    detections = []
    for (x, y, w, h) in faces:
        detections.append(([x, y, w, h], 0.9, 'face'))

    # Tracker update karo
    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()  # left, top, right, bottom
        x1, y1, x2, y2 = map(int, ltrb)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f'ID: {track_id}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow('Person Tracking - Press q to quit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()