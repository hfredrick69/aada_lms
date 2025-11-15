import axios from "axios";

const buildEnvBase = () => {
  const rawValue = import.meta.env.VITE_API_BASE_URL?.trim();
  if (!rawValue) {
    return null;
  }

  let normalized = rawValue.replace(/\/$/, "");
  const isBrowser = typeof window !== "undefined";
  const needsHttps = isBrowser && window.location.protocol === "https:";

  if (isBrowser) {
    try {
      const parsed = new URL(`${normalized}`);
      const dockerHost = window.location.hostname === "host.docker.internal";
      const localhostAlias = ["localhost", "127.0.0.1"].includes(parsed.hostname);
      if (dockerHost && localhostAlias) {
        parsed.hostname = window.location.hostname;
        parsed.protocol = window.location.protocol;
        normalized = parsed.origin;
      }
    } catch {
      // Ignore parse errors and fall back to the raw normalized value
    }
  }

  if (needsHttps && normalized.startsWith("http://")) {
    console.warn("Upgrading VITE_API_BASE_URL to HTTPS to avoid mixed content");
    return `${normalized.replace(/^http:/, "https:")}/api`;
  }

  if (needsHttps && !normalized.startsWith("https://")) {
    console.error("VITE_API_BASE_URL must be HTTPS when the app is served over HTTPS");
    return null;
  }

  return `${normalized}/api`;
};

const inferBrowserBase = () => {
  if (typeof window === "undefined") {
    return "http://localhost:8000/api";
  }

  if (window.location.hostname === "localhost") {
    const apiPort = import.meta.env.VITE_API_PORT || "8000";
    return `${window.location.protocol}//${window.location.hostname}:${apiPort}/api`;
  }

  console.error("VITE_API_BASE_URL missing for production deployment; falling back to localhost");
  return "http://localhost:8000/api";
};

const baseURL = buildEnvBase() || inferBrowserBase();

if (typeof window !== "undefined") {
  window.__AADA_BASE_URL = baseURL;
  console.info("[AADA] API base URL:", baseURL);
}

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
