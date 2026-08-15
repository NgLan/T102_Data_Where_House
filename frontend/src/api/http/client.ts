import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import { handleApiError } from "@/common/errors/handle-api-error";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001/api/v1";

/** Axios client cũ được giữ để các feature chưa chuyển sang generated SDK dùng chung. */
export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-Client-Version": "1.0.0",
  },
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    config.headers.set("X-Request-ID", `req_${crypto.randomUUID()}`);
    return config;
  },
  (error: unknown) => Promise.reject(handleApiError(error)),
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error: unknown) => Promise.reject(handleApiError(error)),
);
