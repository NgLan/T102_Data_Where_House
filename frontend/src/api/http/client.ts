/**
 * Cấu hình Axios Client giao tiếp API với Backend
 * Đảm bảo gắn đầy đủ các Headers chuẩn theo TECHNICAL_CODING_GUIDELINES.md
 */

import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// Lấy Base URL từ biến môi trường hoặc fallback mặc định localhost dev
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Client-Version': '1.0.0',
  },
});

/**
 * Request Interceptor: Tự động sinh X-Request-ID cho mỗi request gửi đi
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const requestId = `req_${Math.random().toString(36).substring(2, 9)}`;
    config.headers.set('X-Request-ID', requestId);
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor: Xử lý tập trung response trả về từ backend
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    // Trả về lỗi đã chuẩn hóa từ backend envelope nếu có
    const apiError = error.response?.data || {
      code: 500,
      message: error.message || 'Lỗi kết nối máy chủ',
      error_code: 'SERVER_CONNECTION_ERROR',
    };
    return Promise.reject(apiError);
  }
);
