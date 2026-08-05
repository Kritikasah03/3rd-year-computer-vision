import "./LogPanel.css";

function LogPanel({ logs, loading }) {
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

      {logs.map((log) => (
        <div key={log.id} className="log-item">
          <span className="log-time">{log.time}</span>

          <span className="log-message">{log.message}</span>
        </div>
      ))}
    </div>
  );
}

export default LogPanel;
