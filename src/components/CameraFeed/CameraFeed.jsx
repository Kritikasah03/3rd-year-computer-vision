import { useEffect, useRef } from "react";
import "./CameraFeed.css";

function CameraFeed() {
  const videoRef = useRef(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Error accessing webcam:", error);
      }
    };

    startCamera();
  }, []);
  return (
    <div className="camera-container">
      <h2>Live Camera Feed</h2>

      {/* <div className="camera-placeholder">
        📷 Camera Offline.
         Waiting for Stream...
      </div> */}

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
      />
    </div>
  );
}

export default CameraFeed;