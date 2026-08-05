import "./ObjectList.css";

function ObjectList({ objects, loading }) {

  if (loading) {
  return (
    <div className="object-list">
      <h2>Detected Objects</h2>
      <p>Loading objects...</p>
    </div>
  );
}
if (!loading && objects.length === 0) {
  return (
    <div className="object-list">
      <h2>Detected Objects</h2>
      <p>No objects detected.</p>
    </div>
  );
}
  return (
    <div className="object-list">
      <h2>Detected Objects</h2>

      {objects.map((object) => (
        <div key={object.id} className="object-item">
          <div className="object-info">
            <span>{object.name}</span>

            <span>{object.confidence}%</span>
          </div>

          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${object.confidence}%`,
              }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ObjectList;
