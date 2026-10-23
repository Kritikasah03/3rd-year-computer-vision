
import "./LogPanel.css";

function LogPanel({ logs = [], loading }) {
  if (loading) {
    return (
      <div className="log-panel">
        <h2>System Logs</h2>
        <p>Loading logs...</p>
      </div>
    );
  }

  return (
    <div className="log-panel">
      <h2>System Logs</h2>

      {logs.length === 0 ? (
        <p>No system logs available.</p>
      ) : (
        logs.map((log, index) => (
          <div
            key={log.id ?? index}
            className="log-item"
          >
            <span className="log-time">
              {log.timestamp
                ? new Date(log.timestamp).toLocaleTimeString()
                : log.time ?? "--:--:--"}
            </span>

            <span className="log-message">
              {log.level ? `[${log.level}] ` : ""}
              {log.message}
            </span>
          </div>
        ))
      )}
    </div>
  );
}

export default LogPanel;