import {
  FaThumbsUp,
  FaThumbsDown,
  FaHandPointer,
  FaHandPeace,
  FaHand,
  FaHandFist,
} from "react-icons/fa6";

import "./HumanoidGesture.css";

const GESTURES = [
  {
    id: "thumbs-up",
    label: "Thumbs Up",
    icon: <FaThumbsUp />,
  },
  {
    id: "thumbs-down",
    label: "Thumbs Down",
    icon: <FaThumbsDown />,
  },
  {
    id: "pointing",
    label: "Pointing",
    icon: <FaHandPointer />,
  },
  {
    id: "peace",
    label: "Peace",
    icon: <FaHandPeace />,
  },
  {
    id: "stop",
    label: "Stop",
    icon: <FaHand />,
  },
  {
    id: "fist",
    label: "Fist",
    icon: <FaHandFist />,
  },
];

function HumanoidGesture({
  detectedGesture = "stop",
}) {
  return (
    <div className="humanoid-gesture">

      {/* HEADER */}
      <div className="gesture-header">
        <div>
          <h2>Gesture Command Set</h2>
        </div>
      </div>

      {/* GESTURE LIST */}
      <div className="gesture-grid">
        {GESTURES.map((gesture) => (
          <div
            key={gesture.id}
            className={`gesture-btn ${
              detectedGesture === gesture.id ? "active" : ""
            }`}
          >
            <span className="gesture-icon">
              {gesture.icon}
            </span>

            <span className="gesture-label">
              {gesture.label}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}

export default HumanoidGesture;