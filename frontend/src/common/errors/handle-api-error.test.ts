import { beforeEach, describe, expect, it } from "vitest";
import errorsVi from "@/common/i18n/locales/vi/errors.json";
import notificationsVi from "@/common/i18n/locales/vi/notifications.json";
import { useNotificationStore } from "@/common/stores/use-notification-store";
import { ApiError } from "./api-error";
import { handleApiError, resolveApiErrorMessage } from "./handle-api-error";

describe("handleApiError", () => {
  beforeEach(() => {
    useNotificationStore.setState({ notifications: [] });
  });

  it("ưu tiên error_code khi tìm bản dịch", () => {
    const error = createError("PROJECT_NOT_FOUND", "not-found", 404);
    expect(resolveApiErrorMessage(error)).toBe(errorsVi.PROJECT_NOT_FOUND);
  });

  it("fallback qua notifications khi error_code chưa được dịch", () => {
    const error = createError("NEW_BACKEND_CODE", "system", 500);
    expect(resolveApiErrorMessage(error)).toBe(notificationsVi.MSG_SYSTEM_ERROR);
  });

  it("phát toast cho lỗi API thường và trả lại normalized error", () => {
    const error = handleApiError({ code: 404, error_code: "PROJECT_NOT_FOUND" });
    expect(error.errorCode).toBe("PROJECT_NOT_FOUND");
    expect(useNotificationStore.getState().notifications).toHaveLength(1);
  });

  it("không toast từng field validation", () => {
    handleApiError({
      code: 422,
      error_code: "INVALID_INPUT_SCHEMA",
      details: [{ field: "name", message: "Required" }],
    });
    expect(useNotificationStore.getState().notifications).toHaveLength(0);
  });
});

/** Tạo normalized error gọn cho các ca kiểm thử message mapping. */
function createError(
  errorCode: string,
  kind: ConstructorParameters<typeof ApiError>[0]["kind"],
  status: number,
): ApiError {
  return new ApiError({
    status,
    errorCode,
    kind,
    message: "",
    details: [],
    originalError: null,
  });
}
