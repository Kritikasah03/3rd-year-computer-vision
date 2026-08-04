import "./ObjectList.css";

function ObjectList({ objects }) {
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
