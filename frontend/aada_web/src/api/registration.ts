import type { AxiosResponse } from "axios";
import { axiosInstance } from "./http-client";

export type RegistrationVerifyResponse = {
  registration_token: string;
  expires_at: string;
};

export const requestRegistration = (email: string): Promise<AxiosResponse> => {
  return axiosInstance({
    url: "/api/auth/register/request",
    method: "POST",
    data: { email },
  });
};

export const verifyRegistration = (token: string): Promise<RegistrationVerifyResponse> => {
  return axiosInstance<RegistrationVerifyResponse>({
    url: "/api/auth/register/verify",
    method: "POST",
    data: { token },
  }).then((response) => response.data);
};

export const completeRegistration = (payload: {
  registration_token: string;
  first_name: string;
  last_name: string;
  password: string;
}): Promise<AxiosResponse> => {
  return axiosInstance({
    url: "/api/auth/register/complete",
    method: "POST",
    data: payload,
  });
};
