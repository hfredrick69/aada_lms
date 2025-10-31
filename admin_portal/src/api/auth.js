import axiosClient from "./axiosClient.js";

export const login = async ({ email, password }) => {
  const response = await axiosClient.post("/auth/login", { email, password });
  return response.data;
};

export const me = async (tokenOverride) => {
  const config = tokenOverride
    ? {
        headers: {
          Authorization: `Bearer ${tokenOverride}`
        }
      }
    : undefined;
  const response = await axiosClient.get("/auth/me", config);
  return response.data;
};
