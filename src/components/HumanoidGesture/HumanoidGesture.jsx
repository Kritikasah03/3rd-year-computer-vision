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
    keywords: ["thumbs up", "thumb_up", "thumbsup"],
  },
  {
    id: "thumbs-down",
    label: "Thumbs Down",
    icon: <FaThumbsDown />,
    keywords: ["thumbs down", "thumb_down", "thumbsdown"],
  },
  {
    id: "pointing",
    label: "Pointing",
    icon: <FaHandPointer />,
    keywords: ["pointing", "point", "point_up", "index"],
  },
  {
    id: "peace",
    label: "Peace",
    icon: <FaHandPeace />,
    keywords: ["peace", "victory", "v_sign"],
  },
  {
    id: "stop",
    label: "Stop",
    icon: <FaHand />,
    keywords: ["stop", "open palm", "open_palm", "palm"],
  },
  {
    id: "fist",
    label: "Fist",
    icon: <FaHandFist />,
    keywords: ["fist", "closed fist", "closed_fist"],
  },
];

const normalizeGesture = (value) =>
  String(value ?? "")
    .toLowerCase()
    .replace(/[_-]+/g, " ")
    .trim();

function HumanoidGesture({ detectedGesture = "", gestureData = null }) {
  const firstGesture = gestureData?.gestures?.[0];

  // The API may return a gesture as a string or as an object.
  const gestureName =
    typeof firstGesture === "string"
      ? firstGesture
      : (firstGesture?.gesture ??
        firstGesture?.label ??
        firstGesture?.name ??
        firstGesture?.class_name ??
        firstGesture?.class ??
        "");

  const activeGesture = normalizeGesture(detectedGesture || gestureName);

  const matchedGesture = GESTURES.find((gesture) =>
    gesture.keywords.some((keyword) =>
      activeGesture.includes(normalizeGesture(keyword)),
    ),
  );

  const handCount = gestureData?.totalHandsDetected ?? 0;
  const activeCommand = gestureData?.activeCommand ?? "STANDBY";

  return (
    <div className="humanoid-gesture">
      <div className="gesture-header">
        <div>
          <h2>Gesture Command Set</h2>
        </div>
      </div>

      <div className="gesture-grid">
        {GESTURES.map((gesture) => (
          <div
            key={gesture.id}
            className={`gesture-btn ${
              matchedGesture?.id === gesture.id ? "active" : ""
            }`}
          >
            <span className="gesture-icon">{gesture.icon}</span>

            <span className="gesture-label">{gesture.label}</span>
          </div>
        ))}
      </div>

      <div className="gesture-status">
        <p>
          <strong>Detected Gesture:</strong> {matchedGesture?.label ?? "None"}
        </p>

        <p>
          <strong>Hands Detected:</strong> {handCount}
        </p>

        <p>
          <strong>Active Command:</strong> {activeCommand}
        </p>

        {gestureData?.message && <p>{gestureData.message}</p>}
      </div>
    </div>
  );
}

export default HumanoidGesture;
