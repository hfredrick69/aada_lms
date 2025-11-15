import axiosClient from "./axiosClient.js";

export const listStudents = async () => {
  const { data } = await axiosClient.get("/students");
  if (Array.isArray(data)) {
    return data;
  }
  if (Array.isArray(data?.students)) {
    return data.students;
  }
  return [];
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
  const { data } = await axiosClient.get(`/enrollments?user_id=${studentId}`);
  return data;
};
