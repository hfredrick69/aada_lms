import axiosClient from "./axiosClient.js";

export const listExternships = async () => {
  const { data } = await axiosClient.get("/externships");
  return data;
};

export const assignExternship = async (payload) => {
  const { data } = await axiosClient.post("/externships", payload);
  return data;
};

export const updateExternship = async (id, payload) => {
  const { data } = await axiosClient.put(`/externships/${id}`, payload);
  return data;
};
