import type { ApiErrorResponse, ErrorDetail } from "../generated/types.gen";
import { ApiError, type ApiErrorDetail } from "./api-error";
import { classifyApiError, defaultErrorCode } from "./classify-api-error";

interface NormalizeApiErrorContext {
  status?: number;
}

type ErrorPayload = Partial<Omit<ApiErrorResponse, "details">> & {
  details?: readonly ApiErrorDetail[];
};

/** Chuẩn hóa lỗi Backend, Fetch và lỗi không xác định về cùng một model. */
export function normalizeApiError(
  error: unknown,
  context: NormalizeApiErrorContext = {},
): ApiError {
  if (error instanceof ApiError) return error;
  const payload = readErrorPayload(error);
  const status = context.status ?? payload.code ?? null;
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
  if (value instanceof Error || !isRecord(value)) return {};
  return {
    code: typeof value.code === "number" ? value.code : undefined,
    message: typeof value.message === "string" ? value.message : undefined,
    error_code:
      typeof value.error_code === "string" ? value.error_code : undefined,
    details: readErrorDetails(value.details),
  };
}

/** Lọc details sai schema thay vì để dữ liệu không an toàn lọt vào UI. */
function readErrorDetails(value: unknown): readonly ApiErrorDetail[] | undefined {
  if (!Array.isArray(value)) return undefined;
  return value.flatMap((item): ApiErrorDetail[] => {
    if (!isRecord(item)) return [];
    const fieldError = readFieldError(item);
    if (fieldError) return [fieldError];
    return [];
  });
}

function readFieldError(item: Record<string, unknown>): ErrorDetail | null {
  if (typeof item.field !== "string" || typeof item.message !== "string") return null;
  return { field: item.field, message: item.message };
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
