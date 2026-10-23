import { useState } from "react";
import EnrolledPersonDatabase from "./EnrolledPersonDatabase/EnrolledPersonDatabase";
import { FaCamera, FaImages, FaRotate } from "react-icons/fa6";
import {
  enrollFace,
  trainFaceModel,
} from "../../services/robotService";
import "./FaceEnrollment.css";

function FaceEnrollment({ videoRef }) {
  const [personName, setPersonName] = useState("");
  const [captureStatus, setCaptureStatus] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [refreshVersion, setRefreshVersion] = useState(0);

  const refreshDatabase = () => {
    setRefreshVersion((version) => version + 1);
  };

  const wait = (ms) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  const captureFrame = () =>
    new Promise((resolve, reject) => {
      const video = videoRef?.current;

      if (
        !video ||
        video.readyState < 2 ||
        !video.videoWidth ||
        !video.videoHeight
      ) {
        reject(
          new Error("Start the camera before capturing a photo.")
        );
        return;
      }

      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext("2d");

      if (!context) {
        reject(new Error("Could not capture the camera frame."));
        return;
      }

      context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
      );

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error("Failed to create the photo."));
            return;
          }

          resolve(
            new File([blob], "face-enrollment.jpg", {
              type: "image/jpeg",
            })
          );
        },
        "image/jpeg",
        0.92
      );
    });

  const handleSinglePhoto = async () => {
    if (!personName.trim()) {
      setCaptureStatus("Enter a person name first.");
      return;
    }

    try {
      setIsProcessing(true);
      setCaptureStatus("Capturing photo...");

      const imageFile = await captureFrame();

      const result = await enrollFace(
        personName.trim(),
        imageFile
      );

      refreshDatabase();

      setCaptureStatus(
        `Enrollment response: ${result || "Success"}`
      );
    } catch (error) {
      setCaptureStatus(
        error.message || "Face enrollment failed."
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRapidCapture = async () => {
    if (!personName.trim()) {
      setCaptureStatus("Enter a person name first.");
      return;
    }

    let successfulCaptures = 0;

    try {
      setIsProcessing(true);

      for (let i = 1; i <= 10; i++) {
        setCaptureStatus(
          `Capturing and enrolling photo ${i}/10...`
        );

        const imageFile = await captureFrame();

        await enrollFace(personName.trim(), imageFile);

        successfulCaptures++;

        if (i < 10) {
          await wait(300);
        }
      }

      setCaptureStatus("Rapid 10x enrollment completed.");
    } catch (error) {
      setCaptureStatus(
        `Enrollment stopped after ${successfulCaptures}/10 photos: ${
          error.message || "Request failed."
        }`
      );
    } finally {
      refreshDatabase();
      setIsProcessing(false);
    }
  };

  const handleTrainModel = async () => {
    try {
      setIsProcessing(true);
      setCaptureStatus("Training model... Please wait.");

      const result = await trainFaceModel();

      let message = result;

      try {
        const parsed = JSON.parse(result);

        if (parsed && typeof parsed === "object") {
          message =
            parsed.message || parsed.detail || result;
        }
      } catch {
        // The response may be plain text.
      }

      refreshDatabase();

      setCaptureStatus(
        `Training response: ${message || "Success"}`
      );
    } catch (error) {
      setCaptureStatus(
        `Training failed: ${
          error.message || "Unknown error"
        }`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="face-enrollment">
      <div className="enrollment-header">
        <div>
          <h2>Face Enrollment</h2>
        </div>
      </div>

      <div className="name-field">
        <label htmlFor="person-name">Person Name</label>

        <input
          id="person-name"
          type="text"
          value={personName}
          onChange={(event) =>
            setPersonName(event.target.value)
          }
          placeholder="Enter person's name"
          disabled={isProcessing}
        />
      </div>

      <div className="enrollment-actions">
        <button
          className="enrollment-btn"
          onClick={handleSinglePhoto}
          disabled={isProcessing}
        >
          <FaCamera className="enrollment-icon" />
          <span>Single Photo</span>
        </button>

        <button
          className="enrollment-btn"
          onClick={handleRapidCapture}
          disabled={isProcessing}
        >
          <FaImages className="enrollment-icon" />
          <span>Rapid 10x</span>
        </button>
      </div>

      <button
        className="train-model-btn"
        onClick={handleTrainModel}
        disabled={isProcessing}
      >
        <FaRotate className="train-icon" />
        <span>Train / Rebuild Model</span>
      </button>

      {captureStatus && (
        <div className="enrollment-status" role="status">
          {captureStatus}
        </div>
      )}

      <div className="enrolled-database-wrapper">
        <EnrolledPersonDatabase
          refreshVersion={refreshVersion}
        />
      </div>
    </div>
  );
}

export default FaceEnrollment;