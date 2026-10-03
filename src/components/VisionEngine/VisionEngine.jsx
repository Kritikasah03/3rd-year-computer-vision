import { useState } from "react";
import "./VisionEngine.css";

const VISION_MODES = [
  {
    id: "full",
    label: "Full Vision Engine",
  },
  {
    id: "face",
    label: "Multi Face Only",
  },
  {
    id: "gesture",
    label: "Gesture Only",
  },
  {
    id: "objects",
    label: "Objects Only",
  },
];

function VisionEngine({ onModeChange }) {
  const [activeMode, setActiveMode] = useState("full");

  const handleModeChange = (mode) => {
    setActiveMode(mode);

    // Send selected mode to the parent.
    // Later the parent can connect this to the backend API.
    if (onModeChange) {
      onModeChange(mode);
    }
  };

  return (
    <div className="vision-engine">

      <div className="vision-mode-grid">
        {VISION_MODES.map((mode) => (
          <button
            key={mode.id}
            className={`vision-mode-btn ${
              activeMode === mode.id ? "active" : ""
            }`}
            onClick={() => handleModeChange(mode.id)}
          >
            {mode.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default VisionEngine;