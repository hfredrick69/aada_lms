import axiosClient from "./axiosClient.js";

export const listStudents = async () => {
  const { data } = await axiosClient.get("/students");
  return data;
};

export const createStudent = async (payload) => {
  const { data } = await axiosClient.post("/students", payload);
  return data;
};

export const updateStudent = async (id, payload) => {
  const { data } = await axiosClient.put(`/students/${id}`, payload);
  return data;
};

export const deleteStudent = async (id) => {
  await axiosClient.delete(`/students/${id}`);
};

export const listEnrollments = async (studentId) => {
  const { data } = await axiosClient.get(`/students/${studentId}/enrollments`);
  return data;
};
