/**
 * Định nghĩa cấu trúc DTO cho API Success & Error Response
 * Tuân thủ theo chuẩn Response Envelope tại TECHNICAL_CODING_GUIDELINES.md
 */

/**
 * Chi tiết lỗi cho từng trường
 */
export interface ErrorDetail {
  field: string;
  message: string;
}

/**
 * Cấu trúc Response khi API thành công (200 OK)
 */
export interface ApiResponse<T> {
  status: 'success';
  code: number;
  message: string;
  data: T;
}

/**
 * Cấu trúc Response khi API gặp lỗi (4xx / 5xx)
 */
export interface ApiErrorResponse {
  code: number;
  message: string;
  error_code: string;
  details?: ErrorDetail[];
}
