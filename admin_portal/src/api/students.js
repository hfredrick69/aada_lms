import axiosClient from "./axiosClient.js";

export const listStudents = async () => {
  const { data } = await axiosClient.get("/users");
  return data;
};

export const createStudent = async (payload) => {
  const { data } = await axiosClient.post("/users", payload);
  return data;
};

export const updateStudent = async (id, payload) => {
  const { data } = await axiosClient.put(`/users/${id}`, payload);
  return data;
};

export const deleteStudent = async (id) => {
  await axiosClient.delete(`/users/${id}`);
};

export const listEnrollments = async (studentId) => {
  const { data } = await axiosClient.get(`/enrollments?user_id=${studentId}`);
  return data;
};
