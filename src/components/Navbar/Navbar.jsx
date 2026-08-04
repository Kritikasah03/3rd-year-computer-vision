import { useState, useEffect } from "react";
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
      <h1>Vision Intelligence Dashboard</h1>

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