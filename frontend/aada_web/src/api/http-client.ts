import axios, { AxiosHeaders } from 'axios';
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
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
});

instance.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    const headers = new AxiosHeaders(config.headers);
    headers.set('Authorization', `Bearer ${token}`);
    config.headers = headers;
  }
  return config;
});

instance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
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
