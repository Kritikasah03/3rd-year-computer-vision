import "./FaceList.css";

function FaceList({ faces, loading }) {

  if (loading) {
  return (
    <div className="face-list">
      <h2>Recognized Faces</h2>
      <p>Loading faces...</p>
    </div>
  );
}
if (!loading && faces.length === 0) {
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

      {faces.map((face) => (
        <div
          key={face.id}
          className="face-item"
        >
          <div className="face-info">
            <span>{face.name}</span>

            <span>
              {face.confidence}%
            </span>
          </div>

          <div className="face-bar">
            <div
              className="face-fill"
              style={{
                width: `${face.confidence}%`,
              }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default FaceList;