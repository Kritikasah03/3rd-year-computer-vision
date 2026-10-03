import { useState } from "react";
import EnrolledPersonDatabase from "./EnrolledPersonDatabase/EnrolledPersonDatabase";
import {
  FaCamera,
  FaImages,
  FaRotate,
} from "react-icons/fa6";

import "./FaceEnrollment.css";

function FaceEnrollment() {
  const [personName, setPersonName] = useState("");
  const [captureStatus, setCaptureStatus] = useState("");

  const handleSinglePhoto = () => {
    if (!personName.trim()) {
      setCaptureStatus("Enter a person name first");
      return;
    }

    setCaptureStatus("Single photo capture ready");
  };

  const handleRapidCapture = () => {
    if (!personName.trim()) {
      setCaptureStatus("Enter a person name first");
      return;
    }

    setCaptureStatus("Rapid 10x capture ready");
  };

  const handleTrainModel = () => {
    setCaptureStatus("Model training will be handled by the backend");
  };

  return (
    <div className="face-enrollment">

      {/* HEADER */}
      <div className="enrollment-header">
        <div>
          <h2>Face Enrollment</h2>
        </div>
      </div>

      {/* PERSON NAME */}
      <div className="name-field">
        <label htmlFor="person-name">
          Person Name
        </label>

        <input
          id="person-name"
          type="text"
          value={personName}
          onChange={(e) => setPersonName(e.target.value)}
          placeholder="Enter person's name"
        />
      </div>

      {/* CAPTURE OPTIONS */}
      <div className="enrollment-actions">

        <button
          className="enrollment-btn"
          onClick={handleSinglePhoto}
        >
          <FaCamera className="enrollment-icon" />

          <span>Single Photo</span>
        </button>

        <button
          className="enrollment-btn"
          onClick={handleRapidCapture}
        >
          <FaImages className="enrollment-icon" />

          <span>Rapid 10x</span>
        </button>

      </div>

      {/* TRAIN MODEL */}
      <button
        className="train-model-btn"
        onClick={handleTrainModel}
      >
        <FaRotate className="train-icon" />

        <span>Train / Rebuild Model</span>
      </button>

      {/* STATUS */}
      {captureStatus && (
        <div className="enrollment-status">
          {captureStatus}
        </div>
      )}
      <div className="enrolled-database-wrapper">
     <EnrolledPersonDatabase />
      </div>

    </div>
    
  );
}

export default FaceEnrollment;