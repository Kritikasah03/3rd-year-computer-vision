import "./Sidebar.css";

import {
  FaTachometerAlt,
  FaCamera,
  FaCube,
  FaUserFriends,
  FaFileAlt,
} from "react-icons/fa";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        VISION AI
      </div>

      <nav className="sidebar-menu">
        <a href="#dashboard" className="menu-item active">
          <FaTachometerAlt />
          <span>Dashboard</span>
        </a>

        <a href="#camera" className="menu-item">
          <FaCamera />
          <span>Camera</span>
        </a>

        <a href="#objects" className="menu-item">
          <FaCube />
          <span>Objects</span>
        </a>

        <a href="#faces" className="menu-item">
          <FaUserFriends />
          <span>Faces</span>
        </a>

        <a href="#logs" className="menu-item">
          <FaFileAlt />
          <span>Logs</span>
        </a>
      </nav>
    </aside>
  );
}

export default Sidebar;