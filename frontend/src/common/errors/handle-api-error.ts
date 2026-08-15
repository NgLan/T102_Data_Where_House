import i18n from "@/common/i18n/i18n";
import notificationsVi from "@/common/i18n/locales/vi/notifications.json";
import { publishNotification } from "@/common/stores/use-notification-store";
import type { ApiError, ApiErrorKind } from "./api-error";
import { normalizeApiError } from "./normalize-api-error";

type NotificationKey = keyof typeof notificationsVi;

interface HandleApiErrorOptions {
  status?: number;
  shouldNotify?: boolean;
}

const notifiedErrors = new WeakSet<ApiError>();

/** Chuẩn hóa, phát toast phù hợp và trả lại lỗi để client tiếp tục reject. */
export function handleApiError(
  error: unknown,
  options: HandleApiErrorOptions = {},
): ApiError {
  const normalized = normalizeApiError(error, { status: options.status });
  if (options.shouldNotify !== false) notifyApiError(normalized);
  return normalized;
}

/** Phát notification cho lỗi chưa được xử lý mà không làm mất lỗi gốc. */
export function notifyApiError(error: ApiError, force = false): void {
  if (!force && (notifiedErrors.has(error) || shouldDeferNotification(error))) return;
  const message = resolveApiErrorMessage(error);
  publishNotification({
    title: i18n.t("TXT_ERROR_TITLE", { ns: "notifications" }),
    message,
    type: "error",
  });
  notifiedErrors.add(error);
}

/** Tra message theo error_code trước, sau đó mới dùng fallback notification. */
export function resolveApiErrorMessage(error: ApiError): string {
  if (i18n.exists(error.errorCode, { ns: "errors" })) {
    return i18n.t(error.errorCode, { ns: "errors" });
  }
  return i18n.t(fallbackKeyByKind(error.kind), { ns: "notifications" });
}

/** Hoãn auth và field validation cho luồng chuyên biệt tương ứng. */
function shouldDeferNotification(error: ApiError): boolean {
  if (error.kind === "authentication") return true;
  return error.kind === "validation" && error.details.length > 0;
}

/** Chọn message notification chung khi error_code chưa có bản dịch. */
function fallbackKeyByKind(kind: ApiErrorKind): NotificationKey {
  const keys: Partial<Record<ApiErrorKind, NotificationKey>> = {
    authorization: "MSG_PERMISSION_DENIED",
    conflict: "MSG_CONFLICT",
    network: "MSG_NETWORK_ERROR",
    "not-found": "MSG_RESOURCE_NOT_FOUND",
    "rate-limit": "MSG_RATE_LIMIT",
    system: "MSG_SYSTEM_ERROR",
    timeout: "MSG_NETWORK_ERROR",
    validation: "MSG_VALIDATION_ERROR",
  };
  return keys[kind] ?? "MSG_ACTION_FAILED";
}
