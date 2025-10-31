import axiosClient from "./axiosClient.js";

export const listPrograms = async () => {
  const { data } = await axiosClient.get("/programs");
  return data;
};

export const listModules = async (programId) => {
  const { data } = await axiosClient.get(`/programs/${programId}/modules`);
  return data;
};

export const progressStats = async () => {
  const { data } = await axiosClient.get("/reports/progress-summary");
  return data;
};
