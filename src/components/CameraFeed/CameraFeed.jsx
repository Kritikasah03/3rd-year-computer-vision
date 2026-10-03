import { useEffect, useRef, useState } from "react";
import "./CameraFeed.css";

function CameraFeed() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [isStreaming, setIsStreaming] = useState(false);

  const startCamera = async () => {
    try {
      // Prevent creating another stream if camera is already running
      if (streamRef.current) {
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      setIsStreaming(true);
    } catch (error) {
      console.error("Error accessing webcam:", error);
      setIsStreaming(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsStreaming(false);
  };

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => {
          track.stop();
        });
      }
    };
  }, []);

  return (
    <div className="camera-container">
      <div className="camera-header">
        <h2>Live Camera Feed</h2>

        <span className={isStreaming ? "camera-status live" : "camera-status"}>
          {isStreaming ? "● LIVE" : "● CAMERA OFF"}
        </span>
      </div>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
      />

      <div className="camera-controls">
        <button
          className="start-camera-btn"
          onClick={startCamera}
          disabled={isStreaming}
        >
          Start Live Camera
        </button>

        <button
          className="stop-camera-btn"
          onClick={stopCamera}
          disabled={!isStreaming}
        >
          Stop Camera
        </button>
      </div>
    </div>
  );
}

export default CameraFeed;