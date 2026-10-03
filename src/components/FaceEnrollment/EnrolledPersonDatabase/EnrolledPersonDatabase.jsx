import {
  FaUser,
  FaTrash,
} from "react-icons/fa6";

import "./EnrolledPersonDatabase.css";

const ENROLLED_PEOPLE = [
  {
    id: 1,
    name: "Person 1",
  },
  {
    id: 2,
    name: "Person 2",
  },
  {
    id: 3,
    name: "Person 3",
  },
  {
    id: 4,
    name: "Person 4",
  },
  {
    id: 5,
    name: "Person 5",
  },
];

function EnrolledPersonDatabase() {
  return (
    <div className="enrolled-database">

      {/* HEADER */}
      <div className="database-header">
        <div>
          <h2>Enrolled Person Database</h2>

        </div>

        <span className="person-count">
          {ENROLLED_PEOPLE.length} Enrolled
        </span>
      </div>

      {/* PERSON LIST */}
      <div className="person-list">
        {ENROLLED_PEOPLE.map((person) => (
          <div
            className="person-item"
            key={person.id}
          >
            {/* AVATAR */}
            <div className="person-avatar">
              <FaUser />
            </div>

            {/* PERSON INFO */}
            <div className="person-info">
              <span className="person-name">
                {person.name}
              </span>

              <span className="person-status">
                Enrolled
              </span>
            </div>

            {/* DELETE BUTTON */}
            <button
              className="delete-person-btn"
              title={`Delete ${person.name}`}
            >
              <FaTrash />
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}

export default EnrolledPersonDatabase;