import "./StatusCard.css";

function StatusCard({
  title,
  value,
  progress,
}) {
  return (
    <div className="status-card">

      <div className="status-header">
        <h3>{title}</h3>
      </div>

      <p className="status-value">
        {value}
      </p>

      <div className="progress-bar">

        <div
          className="progress-fill"
          style={{
            width: `${progress}%`,
          }}
        ></div>

      </div>

    </div>
  );
}

export default StatusCard;