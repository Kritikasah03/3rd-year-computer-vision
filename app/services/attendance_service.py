import csv
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"


class AttendanceService:
    def __init__(self, debounce_seconds: int = 60):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.debounce_seconds = debounce_seconds
        self.last_marked_times: Dict[str, float] = {}
        self.marked_today: set = set()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not ATTENDANCE_FILE.exists():
            with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])

    def mark_attendance_auto(self, person_name: str) -> bool:
        """
        Marks attendance for person with debounce window.
        Returns True if marked now, False if debounced.
        """
        if not person_name or person_name.lower() in ("unknown", "no face detected"):
            return False

        now_timestamp = time.time()
        last_time = self.last_marked_times.get(person_name, 0)

        # Debounce to prevent rapid duplicate writes
        if now_timestamp - last_time < self.debounce_seconds:
            return False

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        try:
            self._ensure_file_exists()
            with open(ATTENDANCE_FILE, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([person_name, date_str, time_str])

            self.last_marked_times[person_name] = now_timestamp
            self.marked_today.add(person_name)
            return True
        except Exception as error:
            print(f"Error marking attendance for {person_name}: {error}")
            return False

    def mark_attendance_manual(self, person_name: str, date_str: Optional[str] = None, time_str: Optional[str] = None) -> Dict[str, Any]:
        if not person_name or not person_name.strip():
            return {"success": False, "message": "Person name cannot be empty."}

        now = datetime.now()
        date_val = date_str if date_str else now.strftime("%Y-%m-%d")
        time_val = time_str if time_str else now.strftime("%H:%M:%S")

        try:
            self._ensure_file_exists()
            with open(ATTENDANCE_FILE, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([person_name.strip(), date_val, time_val])

            self.last_marked_times[person_name.strip()] = time.time()
            self.marked_today.add(person_name.strip())
            return {
                "success": True,
                "message": f"Attendance marked for {person_name}.",
                "record": {
                    "name": person_name.strip(),
                    "date": date_val,
                    "time": time_val
                }
            }
        except Exception as error:
            return {"success": False, "message": str(error)}

    def get_attendance(self, date_filter: Optional[str] = None, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        self._ensure_file_exists()
        records = []
        try:
            with open(ATTENDANCE_FILE, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                header = next(reader, None)
                record_id = 1
                for row in reader:
                    if len(row) >= 3:
                        name, date_val, time_val = row[0].strip(), row[1].strip(), row[2].strip()
                        if date_filter and date_filter != "all" and date_val != date_filter:
                            continue
                        if name_filter and name_filter.lower() not in name.lower():
                            continue
                        records.append({
                            "id": record_id,
                            "name": name,
                            "date": date_val,
                            "time": time_val
                        })
                        record_id += 1
        except Exception as error:
            print(f"Error reading attendance file: {error}")

        # Return latest records first
        records.reverse()
        return records

    def get_today_count(self) -> int:
        today_str = datetime.now().strftime("%Y-%m-%d")
        records = self.get_attendance(date_filter=today_str)
        # Unique persons marked today
        unique_names = {r["name"] for r in records}
        return len(unique_names)

    def clear_attendance(self) -> Dict[str, Any]:
        try:
            with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])
            self.last_marked_times.clear()
            self.marked_today.clear()
            return {"success": True, "message": "Attendance records cleared."}
        except Exception as error:
            return {"success": False, "message": str(error)}
