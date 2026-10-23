import {
  FaThermometerHalf,
  FaMicrochip,
  FaMemory,
  FaWifi,
} from "react-icons/fa";

import { useEffect, useRef, useState } from "react";

import Navbar from "../components/Navbar/Navbar";
import StatusCard from "../components/StatusCard/StatusCard";
import CameraFeed from "../components/CameraFeed/CameraFeed";
import ObjectList from "../components/ObjectList/ObjectList.jsx";
import FaceList from "../components/FaceList/FaceList";
import LogPanel from "../components/LogPanel/LogPanel";
import VisionEngine from "../components/VisionEngine/VisionEngine";
import HumanoidGesture from "../components/HumanoidGesture/HumanoidGesture";
import FaceEnrollment from "../components/FaceEnrollment/FaceEnrollment";

import {
  getRobotStatus,
  getRecognizedFaces,
  getLogs,
  detectObjects,
  recognizeFaces,
  detectGestures,
} from "../services/robotService";

// Accept either internal mode IDs or the labels displayed in the UI.
const normalizeVisionMode = (mode) => {
  const value = String(mode ?? "")
    .toLowerCase()
    .replace(/[_-]/g, " ")
    .trim();

  if (value.includes("gesture")) return "gesture";
  if (value.includes("object")) return "objects";
  if (value.includes("face")) return "face";
  if (value.includes("full")) return "full";

  return "full";
};

function Dashboard() {
  const cameraVideoRef = useRef(null);
  const processingInProgressRef = useRef(false);

  const [loading, setLoading] = useState(true);
  const [isDetectingObjects, setIsDetectingObjects] = useState(false);

  const [status, setStatus] = useState({});
  const [objects, setObjects] = useState([]);
  const [faces, setFaces] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [gestureData, setGestureData] = useState(null);

  const [visionMode, setVisionMode] = useState("full");

  // Load initial telemetry, recognized faces, and logs.
  useEffect(() => {
    let active = true;

    const loadData = async () => {
      try {
        const statusData = await getRobotStatus();

        if (active) {
          setStatus(statusData);
        }
      } catch (error) {
        console.error("Failed to load robot telemetry:", error);
      }

      const results = await Promise.allSettled([
        getRecognizedFaces(),
        getLogs(),
      ]);

      if (!active) return;

      if (results[0].status === "fulfilled") {
        setFaces(results[0].value);
      } else {
        console.error("Failed to load recognized faces:", results[0].reason);
      }

      if (results[1].status === "fulfilled") {
        setSystemLogs(results[1].value);
      } else {
        console.error("Failed to load system logs:", results[1].reason);
      }

      setObjects([]);
      setLoading(false);
    };

    loadData();

    return () => {
      active = false;
    };
  }, []);

  // Immediately clear results belonging to disabled modes.
  const handleVisionModeChange = (mode) => {
    const nextMode = normalizeVisionMode(mode);

    setVisionMode(nextMode);
    console.log("Vision mode changed:", nextMode);

    if (nextMode !== "full" && nextMode !== "face") {
      setFaces([]);
    }

    if (nextMode !== "full" && nextMode !== "objects") {
      setObjects([]);
      setIsDetectingObjects(false);
    }

    if (nextMode !== "full" && nextMode !== "gesture") {
      setGestureData(null);
    }
  };

  // Process camera frames only for the selected vision features.
  useEffect(() => {
    const shouldDetectObjects =
      visionMode === "full" || visionMode === "objects";

    const shouldRecognizeFaces = visionMode === "full" || visionMode === "face";

    const shouldDetectGestures =
      visionMode === "full" || visionMode === "gesture";

    // Clear results from disabled features when the mode changes.
    if (!shouldRecognizeFaces) {
      setFaces([]);
    }

    if (!shouldDetectObjects) {
      setObjects([]);
      setIsDetectingObjects(false);
    }

    if (!shouldDetectGestures) {
      setGestureData(null);
    }

    let active = true;

    const processCameraFrame = async () => {
      const video = cameraVideoRef.current;

      if (
        !video ||
        !video.srcObject ||
        video.readyState < 2 ||
        video.videoWidth === 0 ||
        video.videoHeight === 0 ||
        processingInProgressRef.current
      ) {
        return;
      }

      processingInProgressRef.current = true;

      try {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");

        if (!context) {
          throw new Error("Unable to capture camera frame.");
        }

        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageBlob = await new Promise((resolve, reject) => {
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob);
              } else {
                reject(new Error("Unable to create camera image."));
              }
            },
            "image/jpeg",
            0.85,
          );
        });

        const imageFile = new File([imageBlob], "camera-frame.jpg", {
          type: "image/jpeg",
        });

        // 1. Object detection.
        if (shouldDetectObjects) {
          if (active) setIsDetectingObjects(true);

          try {
            const result = await detectObjects(imageFile);

            if (active) {
              // Support either an array or an API response object.
              setObjects(
                Array.isArray(result) ? result : (result?.objects ?? []),
              );
            }
          } catch (error) {
            if (active) {
              console.error("Object detection failed:", error);
            }
          } finally {
            if (active) setIsDetectingObjects(false);
          }
        }

        // 2. Face recognition runs only in Full Vision or Face Only.
        if (shouldRecognizeFaces) {
          try {
            const result = await recognizeFaces(imageFile);

            if (active) {
              setFaces(Array.isArray(result) ? result : (result?.faces ?? []));
            }
          } catch (error) {
            if (active) {
              console.error("Face recognition failed:", error);
              setFaces([]);
            }
          }
        }

        // 3. Gesture detection runs only in Full Vision or Gesture Only.
        if (shouldDetectGestures) {
          try {
            const result = await detectGestures(imageFile);

            if (active) {
              setGestureData(result);
            }
          } catch (error) {
            if (active) {
              console.error("Gesture detection failed:", error);
              setGestureData(null);
            }
          }
        }
      } catch (error) {
        if (active) {
          console.error("Camera frame processing failed:", error);
        }
      } finally {
        processingInProgressRef.current = false;

        if (active) {
          setIsDetectingObjects(false);
        }
      }
    };

    // Process immediately, then check every two seconds.
    processCameraFrame();

    const intervalId = setInterval(processCameraFrame, 800);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [visionMode]);

  return (
    <div className="app-layout">
      <div className="main-content">
        <Navbar />

        <div id="dashboard" className="dashboard">
          {/* STATUS CARDS */}
          <div className="status-cards-grid">
            <StatusCard
              title="Device Temperature"
              value={
                status.temperature == null ? "N/A" : `${status.temperature}°C`
              }
              progress={
                status.temperature == null
                  ? 0
                  : Math.min(100, Math.max(0, status.temperature))
              }
              icon={<FaThermometerHalf />}
            />

            <StatusCard
              title="CPU"
              value={status.cpu == null ? "N/A" : `${status.cpu}%`}
              progress={status.cpu ?? 0}
              icon={<FaMicrochip />}
            />

            <StatusCard
              title="RAM"
              value={status.ram == null ? "N/A" : `${status.ram}%`}
              progress={status.ram ?? 0}
              icon={<FaMemory />}
            />

            <StatusCard
              title="Network"
              value={status.network ?? "N/A"}
              progress={status.network === "CONNECTED" ? 100 : 0}
              icon={<FaWifi />}
            />
          </div>

          {/* CAMERA, VISION ENGINE, AND SYSTEM LOGS */}
          <div className="camera-monitoring-container">
            <div id="camera">
              <CameraFeed videoRef={cameraVideoRef} faces={faces} />
            </div>

            <div id="vision-engine">
              <VisionEngine onModeChange={handleVisionModeChange} />
            </div>

            <div id="logs">
              <LogPanel logs={systemLogs} loading={loading} />
            </div>
          </div>

          {/* GESTURE + FACE ENROLLMENT */}
          <div className="right-top-section">
            <div id="humanoid-gesture" className="humanoid-gesture-section">
              <HumanoidGesture gestureData={gestureData} />
            </div>

            <div id="face-enrollment" className="face-enrollment-section">
              <FaceEnrollment videoRef={cameraVideoRef} />
            </div>
          </div>

          {/* RECOGNIZED FACES */}
          <div className="faces-section">
            <div id="faces">
              <FaceList faces={faces} loading={loading} />
            </div>
          </div>

          {/* LIVE DETECTED OBJECTS */}
          <div id="objects" className="objects-section">
            <ObjectList objects={objects} loading={loading} />

            {isDetectingObjects && (
              <p className="detection-status">Updating object detections...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
