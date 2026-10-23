import { useEffect, useRef, useState } from "react";
import "./CameraFeed.css";

function CameraFeed({ videoRef, faces = [] }) {
  const internalVideoRef = useRef(null);
  const streamRef = useRef(null);

  const cameraRef = videoRef ?? internalVideoRef;

  const [isStreaming, setIsStreaming] = useState(false);
  const [videoDimensions, setVideoDimensions] = useState({
    width: 0,
    height: 0,
  });

  const faceList = Array.isArray(faces) ? faces : [];

  const updateVideoDimensions = () => {
    const video = cameraRef.current;

    if (video && video.videoWidth > 0 && video.videoHeight > 0) {
      setVideoDimensions({
        width: video.videoWidth,
        height: video.videoHeight,
      });
    }
  };

  const startCamera = async () => {
    try {
      if (streamRef.current) return;

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      const video = cameraRef.current;

      if (video) {
        video.srcObject = stream;
        await video.play();
        updateVideoDimensions();
      }

      setIsStreaming(true);
    } catch (error) {
      console.error("Unable to access camera:", error);
      setIsStreaming(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    const video = cameraRef.current;

    if (video) {
      video.pause();
      video.srcObject = null;
    }

    setIsStreaming(false);
    setVideoDimensions({ width: 0, height: 0 });
  };

  useEffect(() => {
    const video = cameraRef.current;

    if (!video) return undefined;

    video.addEventListener("loadedmetadata", updateVideoDimensions);

    return () => {
      video.removeEventListener("loadedmetadata", updateVideoDimensions);

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, [cameraRef]);

  return (
    <div className="camera-container">
      <div className="camera-header">
        <h2>Camera Feed</h2>

        <span className={`camera-status ${isStreaming ? "live" : "offline"}`}>
          <span className="status-dot" />
          {isStreaming ? "LIVE" : "CAMERA OFF"}
        </span>
      </div>

      <div className="camera-video-wrapper">
        <video
          ref={cameraRef}
          autoPlay
          playsInline
          muted
          onLoadedMetadata={updateVideoDimensions}
        />

        {isStreaming &&
          videoDimensions.width > 0 &&
          videoDimensions.height > 0 && (
            <svg
              className="face-box-overlay"
              viewBox={`0 0 ${videoDimensions.width} ${videoDimensions.height}`}
              preserveAspectRatio="xMidYMid slice"
              aria-label="Detected faces"
            >
              {faceList.map((face, index) => {
                if (!face.box) return null;

                const x = Number(face.box.x);
                const y = Number(face.box.y);
                const w = Number(face.box.w);
                const h = Number(face.box.h);

                if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) {
                  return null;
                }

                const name = face.name || "Unknown";
                const isRecognized = face.isRecognized === true;

                // Green for recognized people, red for unknown people.
                const boxColor = isRecognized ? "#22c55e" : "#ef4444";

                const confidence = Number(face.confidence);

                const confidenceText = Number.isFinite(confidence)
                  ? `${confidence.toFixed(1)}%`
                  : "N/A";

                const label = `${name} ${confidenceText}`;
                const labelWidth = Math.max(110, label.length * 9 + 16);
                const labelHeight = 28;
                const labelY = Math.max(0, y - labelHeight);

                return (
                  <g key={face.id ?? `${name}-${index}`}>
                    {/* Bounding rectangle */}
                    <rect
                      x={x}
                      y={y}
                      width={w}
                      height={h}
                      fill="none"
                      stroke={boxColor}
                      strokeWidth="3"
                    />

                    {/* Name and confidence background */}
                    <rect
                      x={x}
                      y={labelY}
                      width={labelWidth}
                      height={labelHeight}
                      fill={boxColor}
                      rx="3"
                    />

                    {/* Name and confidence text */}
                    <text
                      x={x + 8}
                      y={labelY + 19}
                      fill="#ffffff"
                      fontSize="14"
                      fontWeight="600"
                    >
                      {label}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
      </div>

      <div className="camera-controls">
        {!isStreaming ? (
          <button
            type="button"
            className="start-camera-btn"
            onClick={startCamera}
          >
            Start Camera
          </button>
        ) : (
          <button
            type="button"
            className="stop-camera-btn"
            onClick={stopCamera}
          >
            Stop Camera
          </button>
        )}
      </div>
    </div>
  );
}

export default CameraFeed;
