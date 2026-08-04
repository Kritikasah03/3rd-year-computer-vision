import "./Sidebar.css";

import {
  FaTachometerAlt,
  FaCube,
  FaUserFriends,
  FaFileAlt,
  FaCog,
  FaInfoCircle,
} from "react-icons/fa";

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        VISION AI
      </div>

      <nav className="sidebar-menu">

        <div className="menu-item active">
          <FaTachometerAlt />
          <span>Dashboard</span>
        </div>

        <div className="menu-item">
          <FaCube />
          <span>Objects</span>
        </div>

        <div className="menu-item">
          <FaUserFriends />
          <span>Faces</span>
        </div>

        <div className="menu-item">
          <FaFileAlt />
          <span>Logs</span>
        </div>

        <div className="menu-item">
          <FaCog />
          <span>Settings</span>
        </div>

        <div className="menu-item">
          <FaInfoCircle />
          <span>About</span>
        </div>

      </nav>

    </aside>
  );
}

export default Sidebar;