# 3rd-year-computer-vision
# Face Recognition and Attendance System

This README explains how to set up and run the project.  
All commands are written after === and should be executed in the terminal.

STEP 1. Open terminal and go to the project folder.

=== cd "C:\Users\YourName\Desktop\face_project"

STEP 2. Create a virtual environment.
=== python -m venv 

STEP 3. Activate the virtual environment.

=== venv\Scripts\activate

STEP 4. Install all the required Python packages.

=== pip install -r requirements.txt

STEP 5. Enroll faces before using recognition. The captured face images will be stored in the enrolled_faces folder with clickin s 

=== python enroll_face.py

STEP 6. Train the face recognition model.

=== python face_recognize.py

STEP 7. Run attendance recognition. The detected person's attendance will automatically be saved in attendance.csv.

=== python attendance_recognize.py

STEP 8. To test only face detection without recognition.

=== python face_detect.py

STEP 9. To recognize already enrolled faces.

=== python face_recognize.py

STEP 10. To test face tracking.

=== python face_tracking.py

STEP 11. To run face tracking with recognition together.

=== python tracking_with_recognition.py

Project Features:
- Face Enrollment
- Face Detection
- Face Recognition
- Automatic Attendance System
- Face Tracking
- Face Tracking with Recognition
- Attendance stored in attendance.csv
* The haarcascade_frontalface_default.xml file is required for face detection and should remain in the project folder.
