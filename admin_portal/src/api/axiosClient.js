import axios from "axios";

const envBase = import.meta.env.VITE_API_BASE_URL;
const inferBrowserBase = () => {
  if (typeof window === "undefined") {
    return "http://localhost:8000/api";
  }
  const { protocol, hostname } = window.location;
  const apiPort = import.meta.env.VITE_API_PORT || "8000";
  return `${protocol}//${hostname}:${apiPort}/api`;
};

const baseURL = envBase || inferBrowserBase();

let authToken = null;

export const setAuthToken = (token) => {
  authToken = token;
};

const axiosClient = axios.create({
  baseURL,
  timeout: 15000
});

axiosClient.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("Unauthorized request detected");
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
