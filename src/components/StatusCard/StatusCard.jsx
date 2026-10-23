
import "./StatusCard.css";

function StatusCard({ title, value, progress, icon }) {
  const displayValue =
    value !== undefined && value !== null ? value : "N/A";

  const safeProgress = Number.isFinite(Number(progress))
    ? Math.min(100, Math.max(0, Number(progress)))
    : 0;

  return (
    <div className="status-card">
      <div className="status-header">
        <div className="status-icon">{icon}</div>
        <h3>{title}</h3>
      </div>

      <p className="status-value">{displayValue}</p>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${safeProgress}%` }}
        />
      </div>
    </div>
  );
}

export default StatusCard;