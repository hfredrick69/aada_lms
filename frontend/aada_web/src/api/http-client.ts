import axios from 'axios';
import type {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
} from 'axios';
import { useAuthStore } from '@/stores/auth-store';

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000';

const instance = axios.create({
  baseURL,
  withCredentials: true,  // Enable httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh interceptor for expired access tokens
let isRefreshing = false;
let failedQueue: Array<{ resolve: (value?: unknown) => void; reject: (reason?: unknown) => void }> = [];

const processQueue = (error: Error | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

instance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // If 401 and not already retrying, attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => instance(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh token (cookie-based)
        await instance.post('/api/auth/refresh');
        processQueue();
        isRefreshing = false;
        return instance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error);
        isRefreshing = false;
        useAuthStore.getState().clearSession();
        return Promise.reject(refreshError);
      }
    }

    // For other errors or if refresh failed
    if (error.response?.status === 401) {
      useAuthStore.getState().clearSession();
    }

    return Promise.reject(error);
  },
);

export const axiosInstance = <T = unknown, R = AxiosResponse<T>>(
  config: AxiosRequestConfig,
): Promise<R> => instance.request<T, R>(config);

export type ApiError = AxiosError<{ detail?: string; message?: string }>;
