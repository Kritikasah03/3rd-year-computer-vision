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
  const [status, setStatus] = useState({});
  const [objects, setObjects] = useState([]);
  const [faces, setFaces] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      const statusData = await getRobotStatus();
      const objectData = await getDetectedObjects();
      const faceData = await getRecognizedFaces();
      const logData = await getLogs();

      setStatus(statusData); // update status state
      setObjects(objectData); // update detected objects
      setFaces(faceData); // update faces
      setSystemLogs(logData); // update logs
    };

    loadData();
  }, []); // the function executes only once initially when the webpage is painted

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        <Navbar />

        <div className="dashboard">
          <StatusCard
            title="Battery"
            value={`${status.battery}%`}
            progress={status.battery}
          />

          <StatusCard
            title="CPU"
            value={`${status.cpu}%`}
            progress={status.cpu}
          />

          <StatusCard
            title="RAM"
            value={`${status.ram}%`}
            progress={status.ram}
          />

          <StatusCard title="Network" value={status.network} progress={100} />

          <div className="camera-section">
            <CameraFeed />

            <ObjectList objects={objects} />
          </div>
          <div className="bottom-section">
            <FaceList faces={faces} />

            <LogPanel logs={systemLogs} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
