import { detectedObjects, recognizedFaces, systemLogs } from "../data/mockData";

const API_BASE_URL = "/backend";

const fetchBackendData = async (endpoint) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
};

// Real telemetry from FastAPI
export const getRobotStatus = async () => {
  const data = await fetchBackendData("/api/telemetry/status");

  const edge = data.edge_telemetry ?? {};
  const network = data.network_telemetry ?? {};

  const memoryUsed = Number(edge.memory_used_mb);
  const memoryTotal = Number(edge.memory_total_mb);

  const ram =
    Number.isFinite(memoryUsed) &&
    Number.isFinite(memoryTotal) &&
    memoryTotal > 0
      ? Number(((memoryUsed / memoryTotal) * 100).toFixed(1))
      : null;

  return {
    battery: null,
    cpu: edge.cpu_usage_pct ?? null,
    ram,
    temperature: edge.temperature_c ?? null,
    network: data.network_status ?? network.status ?? "UNKNOWN",
    systemStatus: data.system_status ?? "UNKNOWN",
    cameraStatus: data.camera_status ?? "UNKNOWN",
    aiStatus: data.ai_status ?? "UNKNOWN",
  };
};

// Keep these as mock data temporarily
// until their POST APIs are integrated.
export const getDetectedObjects = async () => {
  return detectedObjects;
};

export const detectObjects = async (imageFile) => {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await fetch(`${API_BASE_URL}/api/vision/objects`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Object detection failed: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.message || "Object detection failed.");
  }

  return (data.objects ?? []).map((object, index) => ({
    id: `${object.label ?? "object"}-${index}`,
    name: object.label ?? "Unknown object",
    confidence: Number(object.confidence ?? 0),
    category: object.category ?? "unknown",
    box: object.box ?? null,
  }));
};

export const getRecognizedFaces = async () => {
  return [];
};

export const recognizeFaces = async (imageFile) => {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await fetch(
    `${API_BASE_URL}/api/vision/process?mode=face_only&include_annotated_image=false`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(`Face recognition failed: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.message || "Face recognition failed.");
  }

  return (data.faces ?? []).map((face, index) => ({
    id: `${face.name ?? "face"}-${index}`,
    name: face.is_recognized ? (face.name ?? "Unknown") : "Unknown",
    confidence: Number(face.confidence ?? 0),
    isRecognized: Boolean(face.is_recognized),
    box: face.box ?? null,
  }));
};

export const getLogs = async () => {
  const logs = await fetchBackendData("/api/telemetry/logs?limit=50");

  if (!Array.isArray(logs)) {
    throw new Error("Invalid system logs response from backend");
  }

  return logs;
};

export const enrollFace = async (personName, imageFile) => {
  const formData = new FormData();

  formData.append("name", personName.trim());
  formData.append("image", imageFile);

  const response = await fetch(`${API_BASE_URL}/api/vision/enroll`, {
    method: "POST",
    body: formData,
  });

  const responseText = await response.text();

  if (!response.ok) {
    throw new Error(
      responseText || `Face enrollment failed: ${response.status}`,
    );
  }

  return responseText;
};

export const getEnrolledPersons = async () => {
  const response = await fetch(`${API_BASE_URL}/api/vision/enrolled-persons`);

  if (!response.ok) {
    throw new Error(`Failed to load enrolled people: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success || !Array.isArray(data.persons)) {
    throw new Error("Invalid enrolled-persons response from backend.");
  }

  return data.persons.map((person, index) => ({
    id: `${person.name}-${index}`,
    name: person.name,
    images: Number(person.images ?? 0),
  }));
};

export const trainFaceModel = async () => {
  const response = await fetch(`${API_BASE_URL}/api/vision/train`, {
    method: "POST",
  });

  const responseText = await response.text();

  if (!response.ok) {
    throw new Error(
      responseText || `Model training failed: ${response.status}`,
    );
  }

  return responseText;
};

export const deleteEnrolledPerson = async (personName) => {
  const response = await fetch(
    `${API_BASE_URL}/api/vision/enrolled-persons/${encodeURIComponent(personName)}`,
    {
      method: "DELETE",
      headers: {
        accept: "*/*",
      },
    },
  );

  if (!response.ok) {
    let message = `Failed to delete person (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || data.message || message;
    } catch {
      // Keep the default error message if the response isn't JSON.
    }

    throw new Error(message);
  }

  const responseText = await response.text();
  return responseText;
};
export const detectGestures = async (imageFile) => {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await fetch(`${API_BASE_URL}/api/vision/gestures`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Gesture detection failed: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.message || "Gesture detection failed.");
  }

  return {
    gestures: data.gestures ?? [],
    totalHandsDetected: data.total_hands_detected ?? 0,
    activeCommand: data.active_command ?? "STANDBY",
    message: data.message ?? "",
  };
};
