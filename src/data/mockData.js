export const robotStatus = {
  battery: 87,
  cpu: 42,
  ram: 58,
  network: "Connected",
};

export const detectedObjects = [
  {
    id: 1,
    name: "Person",
    confidence: 95,
  },
  {
    id: 2,
    name: "Bottle",
    confidence: 88,
  },
  {
    id: 3,
    name: "Chair",
    confidence: 91,
  },
];

export const recognizedFaces = [
  {
    id: 1,
    name: "Khushi",
    status: "Authorized",
    confidence:56,
  },
  {
    id: 3,
    name: "Komal",
    status: "Unauthorized",
    confidence:56,
  },
  {
    id: 3,
    name: "Kritika",
    status: "Unauthorized",
    confidence:56,
  },
  {
    id: 4,
    name: "Goanshi",
    status: "Unauthorized",
    confidence:56,
  },
  {
    id: 5,
    name: "Unknown",
    status: "Unauthorized",
    confidence:56,
  },
];

export const systemLogs = [
  {
    id: 1,
    time: "19:31",
    message: "Person detected",
  },
  {
    id: 2,
    time: "19:32",
    message: "Face recognized",
  },
  {
    id: 3,
    time: "19:33",
    message: "Bottle detected",
  },
  {
    id: 4,
    time: "19:34",
    message: "Robot connected",
  },
  {
    id: 5,
    time: "19:35",
    message: "Gesture recognized",
  },
];
