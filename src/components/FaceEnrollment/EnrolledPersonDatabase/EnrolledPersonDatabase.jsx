import { useCallback, useEffect, useState } from "react";
import { FaUser, FaTrash } from "react-icons/fa6";
import {
  getEnrolledPersons,
  deleteEnrolledPerson,
} from "../../../services/robotService";
import "./EnrolledPersonDatabase.css";

function EnrolledPersonDatabase({ refreshVersion }) {
  const [people, setPeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingPerson, setDeletingPerson] = useState("");

  const loadPeople = useCallback(async () => {
    try {
      setError("");

      const enrolledPeople = await getEnrolledPersons();
      setPeople(enrolledPeople);
    } catch (err) {
      setError(err.message || "Failed to load enrolled people.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPeople();
  }, [loadPeople, refreshVersion]);

  const handleDelete = async (person) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete ${person.name} from the enrolled database?`
    );

    if (!confirmed) return;

    try {
      setDeletingPerson(person.name);
      setError("");

      await deleteEnrolledPerson(person.name);

      // Reload the list after successful deletion.
      await loadPeople();
    } catch (err) {
      setError(err.message || `Failed to delete ${person.name}.`);
    } finally {
      setDeletingPerson("");
    }
  };

  return (
    <div className="enrolled-database">
      <div className="database-header">
        <div>
          <h2>Enrolled Person Database</h2>
        </div>

        <span className="person-count">
          {loading ? "Loading..." : `${people.length} Enrolled`}
        </span>
      </div>

      <div className="person-list">
        {loading && <p>Loading enrolled people...</p>}

        {!loading && error && (
          <p role="alert">{error}</p>
        )}

        {!loading && !error && people.length === 0 && (
          <p>No enrolled people found.</p>
        )}

        {!loading &&
          !error &&
          people.map((person) => (
            <div className="person-item" key={person.id}>
              <div className="person-avatar">
                <FaUser />
              </div>

              <div className="person-info">
                <span className="person-name">
                  {person.name}
                </span>

                <span className="person-status">
                  Enrolled · {person.images} images
                </span>
              </div>

              <button
                className="delete-person-btn"
                title={`Delete ${person.name}`}
                aria-label={`Delete ${person.name}`}
                onClick={() => handleDelete(person)}
                disabled={deletingPerson !== ""}
              >
                {deletingPerson === person.name ? (
                  "..."
                ) : (
                  <FaTrash />
                )}
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}

export default EnrolledPersonDatabase;