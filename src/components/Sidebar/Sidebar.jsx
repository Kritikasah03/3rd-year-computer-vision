import { useState } from "react";
import "./Sidebar.css";

import {
  FaTachometerAlt,
  FaCamera,
  FaCube,
  FaHandPaper,
  FaUserPlus,
  FaUserFriends,
  FaFileAlt,
  FaBars,
} from "react-icons/fa";

function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed((prev) => !prev);
  };

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>

      {/* =========================
          SIDEBAR HEADER
      ========================= */}
      <div className="sidebar-header">

        <div className="sidebar-logo">
          VISION AI
        </div>

        <button
          className="sidebar-toggle"
          onClick={toggleSidebar}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <FaBars />
        </button>

      </div>


      {/* =========================
          SIDEBAR MENU
      ========================= */}
      <nav className="sidebar-menu">

        <a
          href="#dashboard"
          className="menu-item active"
          title="Dashboard"
        >
          <FaTachometerAlt />
          <span>Dashboard</span>
        </a>

        <a
          href="#camera"
          className="menu-item"
          title="Camera"
        >
          <FaCamera />
          <span>Camera</span>
        </a>

        <a
          href="#objects"
          className="menu-item"
          title="Detected Objects"
        >
          <FaCube />
          <span>Objects</span>
        </a>

        <a
          href="#humanoid-gesture"
          className="menu-item"
          title="Detected Gestures"
        >
          <FaHandPaper />
          <span>Gestures</span>
        </a>

        <a
          href="#face-enrollment"
          className="menu-item"
          title="Face Enrollment"
        >
          <FaUserPlus />
          <span>Face Enrollment</span>
        </a>

        <a
          href="#faces"
          className="menu-item"
          title="Recognized Faces"
        >
          <FaUserFriends />
          <span>Faces</span>
        </a>

        <a
          href="#logs"
          className="menu-item"
          title="Logs"
        >
          <FaFileAlt />
          <span>Logs</span>
        </a>

      </nav>

    </aside>
  );
}

export default Sidebar;