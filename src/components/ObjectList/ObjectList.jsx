
import "./ObjectList.css";

function ObjectList({ objects = [], loading }) {
  if (loading) {
    return (
      <div className="object-list">
        <h2>Detected Objects</h2>
        <p>Loading objects...</p>
      </div>
    );
  }

  if (objects.length === 0) {
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

      {objects.map((object, index) => {
        const confidence = Math.min(
          100,
          Math.max(0, Number(object.confidence ?? 0))
        );

        return (
          <div key={object.id ?? index} className="object-item">
            <div className="object-info">
              <span>{object.name ?? object.class_name ?? "Unknown object"}</span>
              <span>{confidence}%</span>
            </div>

            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ObjectList;