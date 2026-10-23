
import "./FaceList.css";

function FaceList({ faces, loading }) {
  const faceList = Array.isArray(faces) ? faces : [];

  if (loading) {
    return (
      <div className="face-list">
        <h2>Recognized Faces</h2>
        <p>Loading faces...</p>
      </div>
    );
  }

  if (faceList.length === 0) {
    return (
      <div className="face-list">
        <h2>Recognized Faces</h2>
        <p>No faces detected.</p>
      </div>
    );
  }

  return (
    <div className="face-list">
      <h2>Recognized Faces</h2>

      {faceList.map((face, index) => (
        <div
          key={face.id ?? `${face.name}-${index}`}
          className="face-item"
        >
          <div className="face-info">
            <span>{face.name}</span>
            <span>{face.confidence}%</span>
          </div>

          <div className="face-bar">
            <div
              className="face-fill"
              style={{
                width: `${Math.min(
                  100,
                  Math.max(0, Number(face.confidence) || 0)
                )}%`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default FaceList;