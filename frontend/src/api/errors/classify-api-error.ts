import type { ErrorDetail } from "../generated/types.gen";
import type { ApiErrorKind } from "./api-error";

interface ApiErrorClassificationInput {
  error: unknown;
  status: number | null;
  errorCode?: string;
  details: readonly ErrorDetail[];
}

/** Phân loại lỗi theo error_code, HTTP status rồi đến loại lỗi kỹ thuật. */
export function classifyApiError(
  input: ApiErrorClassificationInput,
): ApiErrorKind {
  const { details, error, errorCode, status } = input;
  if (errorCode === "DATA_MODEL_REVISION_CONFLICT") return "conflict";
  if (errorCode === "UNAUTHORIZED") return "authentication";
  if (errorCode === "FORBIDDEN" || errorCode === "PERMISSION_DENIED") {
    return "authorization";
  }
  if (errorCode?.endsWith("_NOT_FOUND")) return "not-found";
  if (
    details.length > 0 &&
    (errorCode === "INVALID_INPUT_SCHEMA" || status === 400 || status === 422)
  ) {
    return "validation";
  }
  if (status !== null) return classifyStatus(status);
  return classifyTechnicalError(error) ?? "unknown";
}

/** Chọn error_code ổn định cho lỗi không có Backend envelope. */
export function defaultErrorCode(kind: ApiErrorKind): string {
  if (kind === "network") return "NETWORK_ERROR";
  if (kind === "timeout") return "TIMEOUT_ERROR";
  if (kind === "system") return "INTERNAL_SERVER_ERROR";
  return "UNKNOWN_ERROR";
}

/** Nhận diện lỗi transport trước khi xét HTTP status. */
function classifyTechnicalError(error: unknown): ApiErrorKind | null {
  if (error instanceof DOMException && error.name === "AbortError") return "timeout";
  if (error instanceof TypeError) return "network";
  return null;
}

/** Ánh xạ status HTTP sang hành vi mặc định. */
function classifyStatus(status: number | null): ApiErrorKind {
  if (status === 400 || status === 422) return "business";
  if (status === 401) return "authentication";
  if (status === 403) return "authorization";
  if (status === 404) return "not-found";
  if (status === 409) return "conflict";
  if (status === 429) return "rate-limit";
  if (status !== null && status >= 500) return "system";
  return "unknown";
}
