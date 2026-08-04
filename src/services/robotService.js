import {
  robotStatus,
  detectedObjects,
  recognizedFaces,
  systemLogs,
} from "../data/mockData";

export const getRobotStatus = async () => {
  return robotStatus;
};

export const getDetectedObjects = async () => {
  return detectedObjects;
};

export const getRecognizedFaces = async () => {
  return recognizedFaces;
};

export const getLogs = async () => {
  return systemLogs;
};

//async (asynchronous) it continues to perform the other tasks, and js tells it when the data arrives