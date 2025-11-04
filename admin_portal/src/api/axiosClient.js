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

const axiosClient = axios.create({
  baseURL,
  timeout: 15000,
  withCredentials: true,  // Enable httpOnly cookies
});

// Token refresh interceptor for expired access tokens
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retrying, attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => axiosClient(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh token (cookie-based)
        await axiosClient.post('/auth/refresh');
        processQueue();
        isRefreshing = false;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        isRefreshing = false;
        // Redirect to login or show error
        console.warn("Session expired - please log in again");
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;
