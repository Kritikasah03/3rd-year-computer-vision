
import {
  FaBatteryThreeQuarters,
  FaMicrochip,
  FaMemory,
  FaWifi,
} from "react-icons/fa";


import Navbar from "../components/Navbar/Navbar";
import Sidebar from "../components/Sidebar/Sidebar";
import StatusCard from "../components/StatusCard/StatusCard";
import CameraFeed from "../components/CameraFeed/CameraFeed";
import ObjectList from "../components/ObjectList/ObjectList.jsx";
import FaceList from "../components/FaceList/FaceList";
import LogPanel from "../components/LogPanel/LogPanel";

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
  }, []); // the function executes only once initially when the webpage is painted

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        <Navbar />

        <div id="dashboard" className="dashboard">
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
            value={status.network} progress={100}
            icon={<FaWifi />} />

          <div className="camera-section">
            <div id="camera">
              <CameraFeed />
            </div>

            <div id="objects">
              <ObjectList objects={objects} loading={loading} />
            </div>
          </div>

          <div className="bottom-section">
            <div id="faces">
              <FaceList faces={faces} loading={loading} />
            </div>

            <div id="logs">
              <LogPanel logs={systemLogs} loading={loading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
