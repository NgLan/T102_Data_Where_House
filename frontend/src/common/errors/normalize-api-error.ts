import axios from "axios";
import { ApiError, type FieldError } from "./api-error";
import { classifyApiError, defaultErrorCode } from "./classify-api-error";

interface NormalizeApiErrorContext {
  status?: number;
}

interface ErrorPayload {
  code?: number;
  message?: string;
  error_code?: string;
  details?: readonly FieldError[];
}

/** Chuẩn hóa lỗi Backend, Axios, Fetch và lỗi không xác định về cùng một model. */
export function normalizeApiError(
  error: unknown,
  context: NormalizeApiErrorContext = {},
): ApiError {
  if (error instanceof ApiError) return error;
  const axiosError = axios.isAxiosError(error) ? error : null;
  const rawPayload = axiosError?.response?.data ?? error;
  const payload = readErrorPayload(rawPayload);
  const status = context.status ?? axiosError?.response?.status ?? payload.code ?? null;
  const details = payload.details ?? [];
  const kind = classifyApiError({
    error,
    status,
    errorCode: payload.error_code,
    details,
  });
  return new ApiError({
    status,
    errorCode:
      payload.error_code ?? readStableErrorCode(error) ?? defaultErrorCode(kind),
    message: payload.message ?? readTechnicalMessage(error),
    details,
    kind,
    originalError: error,
  });
}

/** Đọc Backend envelope từ giá trị không tin cậy. */
function readErrorPayload(value: unknown): ErrorPayload {
  if (!isRecord(value)) return {};
  return {
    code: typeof value.code === "number" ? value.code : undefined,
    message: typeof value.message === "string" ? value.message : undefined,
    error_code:
      typeof value.error_code === "string" ? value.error_code : undefined,
    details: readFieldErrors(value.details),
  };
}

/** Lọc details sai schema thay vì để dữ liệu không an toàn lọt vào UI. */
function readFieldErrors(value: unknown): readonly FieldError[] | undefined {
  if (!Array.isArray(value)) return undefined;
  return value.flatMap((item): FieldError[] => {
    if (!isRecord(item)) return [];
    if (typeof item.field !== "string" || typeof item.message !== "string") return [];
    return [{ field: item.field, message: item.message }];
  });
}

/** Giữ technical message cho logging/caller nhưng không hiển thị trực tiếp. */
function readTechnicalMessage(error: unknown): string {
  return error instanceof Error ? error.message : "";
}

/** Nhận diện Error local chứa mã ổn định thay vì câu chữ hiển thị. */
function readStableErrorCode(error: unknown): string | null {
  if (!(error instanceof Error)) return null;
  return /^[A-Z][A-Z0-9_]+$/.test(error.message) ? error.message : null;
}

/** Kiểm tra object record trước khi đọc các thuộc tính động. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
