import {
  FaBatteryThreeQuarters,
  FaMicrochip,
  FaMemory,
  FaWifi,
} from "react-icons/fa";

import Navbar from "../components/Navbar/Navbar";
import StatusCard from "../components/StatusCard/StatusCard";
import CameraFeed from "../components/CameraFeed/CameraFeed";
import ObjectList from "../components/ObjectList/ObjectList.jsx";
import FaceList from "../components/FaceList/FaceList";
import LogPanel from "../components/LogPanel/LogPanel";
import VisionEngine from "../components/VisionEngine/VisionEngine";
import HumanoidGesture from "../components/HumanoidGesture/HumanoidGesture";
import FaceEnrollment from "../components/FaceEnrollment/FaceEnrollment";

import { useEffect, useState } from "react";

import {
  getRobotStatus,
  getDetectedObjects,
  getRecognizedFaces,
  getLogs,
} from "../services/robotService";

function Dashboard() {
  const [loading, setLoading] = useState(true);

  const [status, setStatus] = useState({});
  const [objects, setObjects] = useState([]);
  const [faces, setFaces] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);

  const [visionMode, setVisionMode] = useState("full");

  useEffect(() => {
    const loadData = async () => {
      try {
        const statusData = await getRobotStatus();
        const objectData = await getDetectedObjects();
        const faceData = await getRecognizedFaces();
        const logData = await getLogs();

        setStatus(statusData);
        setObjects(objectData);
        setFaces(faceData);
        setSystemLogs(logData);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleVisionModeChange = (mode) => {
    setVisionMode(mode);

    console.log("Vision mode changed:", mode);

    // Backend integration will be added here later.
  };

  return (
    <div className="app-layout">

      <div className="main-content">

        <Navbar />

        <div id="dashboard" className="dashboard">

          {/* ==================================================
              STATUS CARDS
          ================================================== */}

          <div className="status-cards-grid">

            <StatusCard
              title="Battery"
              value={`${status.battery}%`}
              progress={status.battery}
              icon={<FaBatteryThreeQuarters />}
            />

            <StatusCard
              title="CPU"
              value={`${status.cpu}%`}
              progress={status.cpu}
              icon={<FaMicrochip />}
            />

            <StatusCard
              title="RAM"
              value={`${status.ram}%`}
              progress={status.ram}
              icon={<FaMemory />}
            />

            <StatusCard
              title="Network"
              value={status.network}
              progress={100}
              icon={<FaWifi />}
            />

          </div>


          {/* ==================================================
              CAMERA MONITORING
          ================================================== */}

          <div className="camera-monitoring-container">

            {/* CAMERA FEED */}

            <div id="camera">
              <CameraFeed />
            </div>


            {/* VISION ENGINE */}

            <div id="vision-engine">
              <VisionEngine
                onModeChange={handleVisionModeChange}
              />
            </div>


            {/* SYSTEM LOGS */}

            <div id="logs">
              <LogPanel
                logs={systemLogs}
                loading={loading}
              />
            </div>

          </div>


          {/* ==================================================
              RIGHT SIDE
              GESTURE + FACE ENROLLMENT
          ================================================== */}

          <div className="right-top-section">

            {/* HUMANOID GESTURE */}

            <div
              id="humanoid-gesture"
              className="humanoid-gesture-section"
            >
              <HumanoidGesture />
            </div>


            {/* FACE ENROLLMENT */}

            <div
              id="face-enrollment"
              className="face-enrollment-section"
            >
              <FaceEnrollment />
            </div>

          </div>


          {/* ==================================================
              RECOGNIZED FACES
          ================================================== */}

          <div className="faces-section">

            <div id="faces">
              <FaceList
                faces={faces}
                loading={loading}
              />
            </div>

          </div>


          {/* ==================================================
              DETECTED OBJECTS
          ================================================== */}

          <div
            id="objects"
            className="objects-section"
          >
            <ObjectList
              objects={objects}
              loading={loading}
            />
          </div>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;