import axiosClient from "./axiosClient.js";

// ============ PROGRAMS ============

export const listPrograms = async () => {
  const { data } = await axiosClient.get("/programs");
  return data;
};

export const getProgram = async (programId) => {
  const { data } = await axiosClient.get(`/programs/${programId}`);
  return data;
};

export const createProgram = async (programData) => {
  const { data } = await axiosClient.post("/programs", programData);
  return data;
};

export const updateProgram = async (programId, programData) => {
  const { data } = await axiosClient.put(`/programs/${programId}`, programData);
  return data;
};

export const deleteProgram = async (programId) => {
  const { data } = await axiosClient.delete(`/programs/${programId}`);
  return data;
};

// ============ MODULES ============

export const listModules = async (programId) => {
  const { data } = await axiosClient.get(`/programs/${programId}/modules`);
  return data;
};

export const getModule = async (programId, moduleId) => {
  const { data } = await axiosClient.get(`/programs/${programId}/modules/${moduleId}`);
  return data;
};

export const createModule = async (programId, moduleData) => {
  const { data } = await axiosClient.post(`/programs/${programId}/modules`, moduleData);
  return data;
};

export const updateModule = async (programId, moduleId, moduleData) => {
  const { data} = await axiosClient.put(`/programs/${programId}/modules/${moduleId}`, moduleData);
  return data;
};

export const deleteModule = async (programId, moduleId) => {
  const { data } = await axiosClient.delete(`/programs/${programId}/modules/${moduleId}`);
  return data;
};

// ============ REPORTS ============

export const progressStats = async () => {
  const { data } = await axiosClient.get("/reports/progress-summary");
  return data;
};
