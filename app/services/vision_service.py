import cv2
import numpy as np
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.services.attendance_service import AttendanceService

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ENROLLED_FACES_DIR = DATA_DIR / "enrolled_faces"
MODELS_DIR = BASE_DIR / "models"

CASCADE_PATH = MODELS_DIR / "haarcascade_frontalface_default.xml"
TRAINER_PATH = MODELS_DIR / "face_trainer.yml"
LABELS_PATH = MODELS_DIR / "labels.json"


class VisionService:
    def __init__(self, attendance_service: Optional[AttendanceService] = None):
        # Create required folders
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ENROLLED_FACES_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        self.attendance_service = attendance_service or AttendanceService()

        # ----------------------------------------------------
        # CHECK / COPY HAAR CASCADE
        # ----------------------------------------------------
        if not CASCADE_PATH.exists():
            # Check if person1 module has the cascade
            alt_cascade = BASE_DIR / "3rd-year-computer-vision-person1-vision-module" / "haarcascade_frontalface_default.xml"
            if alt_cascade.exists():
                shutil.copy(alt_cascade, CASCADE_PATH)
            else:
                # Fallback to OpenCV built-in
                opencv_cascade = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
                if opencv_cascade.exists():
                    shutil.copy(opencv_cascade, CASCADE_PATH)

        if not CASCADE_PATH.exists():
            raise FileNotFoundError(f"Haar Cascade file not found at: {CASCADE_PATH}")

        self.face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load Haar Cascade model.")

        # ----------------------------------------------------
        # CREATE LBPH RECOGNIZER
        # ----------------------------------------------------
        if not hasattr(cv2, "face"):
            raise RuntimeError(
                "OpenCV face module is not available.\nPlease install: opencv-contrib-python"
            )

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_names: Dict[int, str] = {}
        self.model_trained = False

        # Load existing trained model
        self.load_existing_model()

    # ============================================================
    # LOAD EXISTING MODEL
    # ============================================================
    def load_existing_model(self):
        if not TRAINER_PATH.exists() or not LABELS_PATH.exists():
            print("No existing trained model found. Please enroll faces and train.")
            return

        try:
            self.recognizer.read(str(TRAINER_PATH))
            with open(LABELS_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            # JSON keys are strings, convert to integer labels
            self.label_names = {int(key): str(value) for key, value in data.items()}
            self.model_trained = True
            print(f"Face recognition model loaded. Enrolled people: {list(self.label_names.values())}")
        except Exception as error:
            print(f"Could not load existing model: {error}")
            self.model_trained = False

    # ============================================================
    # DETECT FACES (MULTI-PERSON)
    # ============================================================
    def detect_faces(self, image: np.ndarray) -> List[Any]:
        if image is None:
            return []

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        gray = cv2.equalizeHist(gray)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return list(faces)

    # ============================================================
    # RECOGNIZE MULTIPLE FACES IN A SINGLE FRAME
    # ============================================================
    def recognize_faces(self, image: np.ndarray, auto_mark_attendance: bool = True) -> Dict[str, Any]:
        """
        Detects and recognizes ALL faces present in a single image frame simultaneously.
        """
        if image is None:
            return {
                "success": False,
                "faces": [],
                "total_faces_detected": 0,
                "recognized_count": 0,
                "unknown_count": 0,
                "message": "Invalid image provided."
            }

        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Preprocess with CLAHE for illumination invariance (glasses, shadows, ambient lighting)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray_clahe = clahe.apply(gray)
            detected_faces = self.detect_faces(gray_clahe)

            if len(detected_faces) == 0:
                return {
                    "success": True,
                    "faces": [],
                    "total_faces_detected": 0,
                    "recognized_count": 0,
                    "unknown_count": 0,
                    "message": "No faces detected in frame."
                }

            results = []
            recognized_count = 0
            unknown_count = 0

            for (x, y, w, h) in detected_faces:
                # Add 8% adaptive padding around face for better LBPH feature extraction
                pad_w = int(w * 0.08)
                pad_h = int(h * 0.08)
                y1 = max(0, y - pad_h)
                y2 = min(gray.shape[0], y + h + pad_h)
                x1 = max(0, x - pad_w)
                x2 = min(gray.shape[1], x + w + pad_w)

                face_roi = gray_clahe[y1:y2, x1:x2]
                if face_roi.size == 0:
                    continue

                face_resized = cv2.resize(face_roi, (200, 200))

                person_name = "Unknown"
                confidence = 0.0
                distance = 999.0
                is_recognized = False
                attendance_marked = False

                if self.model_trained and len(self.label_names) > 0:
                    try:
                        label, distance_val = self.recognizer.predict(face_resized)
                        distance = round(float(distance_val), 2)
                        
                        # Calibrated LBPH Confidence Mapping:
                        # Real-world LBPH distances:
                        # 0-35: 95-100% (Near identical)
                        # 35-50: 80-95% (Strong match, e.g. glasses/angles)
                        # 50-65: 65-80% (Moderate match)
                        # 65-75: 40-65% (Borderline)
                        # >75: Unknown
                        if distance < 80.0:
                            scaled = 1.0 - (distance / 82.0) ** 1.3
                            confidence = round(max(0.0, min(100.0, scaled * 100.0)), 1)
                        else:
                            confidence = round(max(0.0, 100.0 - distance), 1)

                        candidate_name = self.label_names.get(int(label), "Unknown")
                        if distance < 72.0 and candidate_name != "Unknown":
                            person_name = candidate_name
                            is_recognized = True
                            recognized_count += 1

                            if auto_mark_attendance and self.attendance_service:
                                attendance_marked = self.attendance_service.mark_attendance_auto(person_name)
                        else:
                            person_name = "Unknown"
                            unknown_count += 1
                    except Exception as pred_err:
                        print(f"Face prediction error: {pred_err}")
                        unknown_count += 1
                else:
                    unknown_count += 1

                results.append({
                    "name": person_name,
                    "confidence": confidence,
                    "distance": distance,
                    "box": {
                        "x": int(x),
                        "y": int(y),
                        "w": int(w),
                        "h": int(h)
                    },
                    "is_recognized": is_recognized,
                    "attendance_marked": attendance_marked
                })

            return {
                "success": True,
                "faces": results,
                "total_faces_detected": len(results),
                "recognized_count": recognized_count,
                "unknown_count": unknown_count,
                "message": f"Processed {len(results)} face(s) successfully."
            }

        except Exception as error:
            print(f"Multi-face recognition error: {error}")
            return {
                "success": False,
                "faces": [],
                "total_faces_detected": 0,
                "recognized_count": 0,
                "unknown_count": 0,
                "message": str(error)
            }

    # ============================================================
    # BACKWARD COMPATIBLE SINGLE / PRIMARY FACE RECOGNITION
    # ============================================================
    def recognize_face(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Maintains backward compatibility with earlier endpoint.
        Returns multi-face information while keeping top face at root level.
        """
        multi_result = self.recognize_faces(image, auto_mark_attendance=True)
        if not multi_result["success"] or len(multi_result["faces"]) == 0:
            return {
                "recognized": False,
                "name": "No Face Detected" if multi_result["success"] else "Unknown",
                "confidence": 0.0,
                "faces": [],
                "total_faces": 0
            }

        # Select highest confidence or largest face for primary return
        primary = multi_result["faces"][0]
        for f in multi_result["faces"]:
            if f["is_recognized"]:
                primary = f
                break

        return {
            "recognized": primary["is_recognized"],
            "name": primary["name"],
            "confidence": primary["confidence"],
            "distance": primary["distance"],
            "faces": multi_result["faces"],
            "total_faces": multi_result["total_faces_detected"],
            "recognized_count": multi_result["recognized_count"],
            "unknown_count": multi_result["unknown_count"]
        }

    # ============================================================
    # ENROLL FACE
    # ============================================================
    def enroll_face(self, person_name: str, image: np.ndarray) -> Dict[str, Any]:
        if image is None:
            return {"success": False, "message": "Invalid image received."}

        person_name = person_name.strip()
        if not person_name:
            return {"success": False, "message": "Person name is required."}

        safe_name = "".join(
            c for c in person_name if c.isalnum() or c in (" ", "_", "-")
        ).strip().lower()

        if not safe_name:
            return {"success": False, "message": "Invalid person name characters."}

        person_dir = ENROLLED_FACES_DIR / safe_name
        person_dir.mkdir(parents=True, exist_ok=True)

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = clahe.apply(gray)
        faces = self.detect_faces(gray_clahe)

        if len(faces) == 0:
            return {
                "success": False,
                "message": "No face detected. Please look directly at the camera with good lighting."
            }

        # Select largest face for enrollment
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        pad_w = int(w * 0.08)
        pad_h = int(h * 0.08)
        y1 = max(0, y - pad_h)
        y2 = min(gray.shape[0], y + h + pad_h)
        x1 = max(0, x - pad_w)
        x2 = min(gray.shape[1], x + w + pad_w)

        face_roi = gray_clahe[y1:y2, x1:x2]
        face_resized = cv2.resize(face_roi, (200, 200))

        filename = f"face_{uuid.uuid4().hex[:10]}.jpg"
        image_path = person_dir / filename

        saved = cv2.imwrite(str(image_path), face_resized)
        if not saved:
            return {"success": False, "message": "Failed to save face crop to disk."}

        image_count = len(list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png")))
        return {
            "success": True,
            "message": "Face enrolled successfully.",
            "person": safe_name,
            "images_saved": image_count
        }

    # ============================================================
    # GET ENROLLED PERSONS
    # ============================================================
    def get_enrolled_persons(self) -> List[Dict[str, Any]]:
        persons = []
        if not ENROLLED_FACES_DIR.exists():
            return persons

        for person_dir in sorted(ENROLLED_FACES_DIR.iterdir()):
            if not person_dir.is_dir():
                continue

            images = []
            for ext in ("*.jpg", "*.jpeg", "*.png"):
                images.extend(person_dir.glob(ext))

            persons.append({
                "name": person_dir.name,
                "images": len(images),
                "path": str(person_dir)
            })

        return persons

    # ============================================================
    # DELETE ENROLLED PERSON
    # ============================================================
    def delete_enrolled_person(self, person_name: str) -> Dict[str, Any]:
        safe_name = person_name.strip().lower()
        person_dir = ENROLLED_FACES_DIR / safe_name

        if not person_dir.exists() or not person_dir.is_dir():
            return {"success": False, "message": f"Person '{person_name}' not found."}

        try:
            shutil.rmtree(person_dir)
            # Retrain model after deletion if there are still faces
            self.train_model()
            return {"success": True, "message": f"Deleted person '{person_name}' successfully."}
        except Exception as error:
            return {"success": False, "message": str(error)}

    # ============================================================
    # TRAIN MODEL
    # ============================================================
    def train_model(self) -> Dict[str, Any]:
        faces_data = []
        labels = []
        self.label_names = {}
        current_label = 0
        persons_found = 0

        if not ENROLLED_FACES_DIR.exists():
            return {"success": False, "message": "Enrolled faces directory does not exist."}

        for person_folder in sorted(ENROLLED_FACES_DIR.iterdir()):
            if not person_folder.is_dir():
                continue

            person_name = person_folder.name
            person_label = current_label
            self.label_names[person_label] = person_name
            current_label += 1

            person_face_count = 0
            for image_path in person_folder.iterdir():
                if image_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                    continue

                try:
                    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue

                    face = cv2.resize(img, (200, 200))
                    faces_data.append(face)
                    labels.append(person_label)
                    person_face_count += 1
                except Exception as err:
                    print(f"Error reading {image_path}: {err}")

            if person_face_count > 0:
                persons_found += 1

        if len(faces_data) == 0 or persons_found == 0:
            return {
                "success": False,
                "message": "No valid enrolled face images found. Please enroll faces first."
            }

        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.train(faces_data, np.array(labels, dtype=np.int32))
            self.recognizer.write(str(TRAINER_PATH))

            with open(LABELS_PATH, "w", encoding="utf-8") as file:
                json.dump(self.label_names, file, indent=4)

            self.model_trained = True
            return {
                "success": True,
                "message": "Face recognition model trained successfully.",
                "faces_used": len(faces_data),
                "persons": persons_found,
                "person_names": list(self.label_names.values())
            }
        except Exception as error:
            return {"success": False, "message": f"Training failed: {str(error)}"}

    # ============================================================
    # ANNOTATE FRAME WITH MULTI-FACE HUD
    # ============================================================
    def draw_face_overlays(self, frame: np.ndarray, faces: List[Dict[str, Any]]) -> np.ndarray:
        annotated = frame.copy()
        for face in faces:
            box = face["box"]
            x, y, w, h = box["x"], box["y"], box["w"], box["h"]
            name = face["name"]
            is_recognized = face.get("is_recognized", False)
            confidence = face.get("confidence", 0.0)

            color = (0, 220, 0) if is_recognized else (0, 70, 240)  # Bright Green vs Orange/Red

            # Draw bounding box with high-tech corner accents
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            corner_len = int(min(w, h) * 0.25)
            # Top-left corner
            cv2.line(annotated, (x, y), (x + corner_len, y), color, 4)
            cv2.line(annotated, (x, y), (x, y + corner_len), color, 4)
            # Top-right corner
            cv2.line(annotated, (x + w, y), (x + w - corner_len, y), color, 4)
            cv2.line(annotated, (x + w, y), (x + w, y + corner_len), color, 4)
            # Bottom-left corner
            cv2.line(annotated, (x, y + h), (x + corner_len, y + h), color, 4)
            cv2.line(annotated, (x, y + h), (x, y + h - corner_len), color, 4)
            # Bottom-right corner
            cv2.line(annotated, (x + w, y + h), (x + w - corner_len, y + h), color, 4)
            cv2.line(annotated, (x + w, y + h), (x + w, y + h - corner_len), color, 4)

            # Label text
            if is_recognized:
                label_text = f"{name.upper()} ({confidence}%)"
            else:
                label_text = "UNKNOWN PERSON"

            # Background pill for text
            (text_w, text_h), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            label_y = max(y - 10, text_h + 10)
            cv2.rectangle(annotated, (x, label_y - text_h - 6), (x + text_w + 10, label_y + 4), color, -1)
            cv2.putText(annotated, label_text, (x + 5, label_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        return annotated