import { useState, useEffect } from "react";

import {
  FaTachometerAlt,
  FaCamera,
  FaCube,
  FaHandPaper,
  FaUserPlus,
  FaUserFriends,
  FaFileAlt,
} from "react-icons/fa";

import "./Navbar.css";

function Navbar() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <header className="navbar">

      {/* LOGO */}
      <div className="navbar-logo">
        VISION AI
      </div>

      {/* NAVIGATION */}
      <nav className="navbar-menu">

        <a
          href="#dashboard"
          className="navbar-item active"
        >
          <FaTachometerAlt />
          <span>Dashboard</span>
        </a>

        <a
          href="#camera"
          className="navbar-item"
        >
          <FaCamera />
          <span>Camera</span>
        </a>

        <a
          href="#objects"
          className="navbar-item"
        >
          <FaCube />
          <span>Objects</span>
        </a>

        <a
          href="#humanoid-gesture"
          className="navbar-item"
        >
          <FaHandPaper />
          <span>Gestures</span>
        </a>

        <a
          href="#face-enrollment"
          className="navbar-item"
        >
          <FaUserPlus />
          <span>Face Enrollment</span>
        </a>

        <a
          href="#faces"
          className="navbar-item"
        >
          <FaUserFriends />
          <span>Faces</span>
        </a>

        <a
          href="#logs"
          className="navbar-item"
        >
          <FaFileAlt />
          <span>Logs</span>
        </a>

      </nav>

      {/* RIGHT SIDE */}
      <div className="navbar-right">

        <span className="connected">
          ● Robot Connected
        </span>

        <div className="date-time">

          <span>
            {currentTime.toLocaleDateString()}
          </span>

          <span>
            {currentTime.toLocaleTimeString()}
          </span>

        </div>

      </div>

    </header>
  );
}

export default Navbar;