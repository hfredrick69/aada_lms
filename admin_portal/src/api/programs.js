import axiosClient from "./axiosClient.js";

export const listPrograms = async () => {
  const { data } = await axiosClient.get("/programs");
  return data;
};
