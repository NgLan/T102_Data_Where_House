/** Nhóm lỗi chuẩn hóa quyết định cách giao diện phản hồi. */
export type ApiErrorKind =
  | "authentication"
  | "authorization"
  | "business"
  | "conflict"
  | "network"
  | "not-found"
  | "rate-limit"
  | "system"
  | "timeout"
  | "unknown"
  | "validation";

/** Chi tiết lỗi gắn với một field do Backend trả về. */
export interface FieldError {
  field: string;
  message: string;
}

/** Dữ liệu đầu vào để khởi tạo lỗi API đã chuẩn hóa. */
export interface ApiErrorInput {
  status: number | null;
  errorCode: string;
  message: string;
  details: readonly FieldError[];
  kind: ApiErrorKind;
  originalError: unknown;
}

/** Lỗi API thống nhất được reject cho mọi caller sau khi qua client dùng chung. */
export class ApiError extends Error {
  readonly status: number | null;
  readonly errorCode: string;
  readonly details: readonly FieldError[];
  readonly kind: ApiErrorKind;
  readonly originalError: unknown;

  constructor(input: ApiErrorInput) {
    super(input.message);
    this.name = "ApiError";
    this.status = input.status;
    this.errorCode = input.errorCode;
    this.details = input.details;
    this.kind = input.kind;
    this.originalError = input.originalError;
  }
}

/** Lỗi validation có danh sách field hợp lệ để form tiêu thụ. */
export interface ApiValidationError extends ApiError {
  readonly kind: "validation";
  readonly details: readonly FieldError[];
}

/** Kiểm tra một giá trị đã là lỗi API chuẩn hóa hay chưa. */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/** Kiểm tra lỗi validation có thể chuyển tiếp cho form. */
export function isApiValidationError(
  error: ApiError,
): error is ApiValidationError {
  return error.kind === "validation" && error.details.length > 0;
}
