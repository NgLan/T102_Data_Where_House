import { beforeEach, describe, expect, it, vi } from "vitest";
import errorsVi from "@/common/i18n/locales/vi/errors.json";
import notificationsVi from "@/common/i18n/locales/vi/notifications.json";
import { notifyAppError } from "@/common/notifications";
import { ApiError } from "./api-error";
import { handleApiError, resolveApiErrorMessage } from "./handle-api-error";

vi.mock("@/common/notifications", () => ({
  notifyAppError: vi.fn(),
}));

describe("handleApiError", () => {
  beforeEach(() => {
    vi.mocked(notifyAppError).mockClear();
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
    expect(notifyAppError).toHaveBeenCalledOnce();
  });

  it("không toast từng field validation", () => {
    handleApiError({
      code: 422,
      error_code: "INVALID_INPUT_SCHEMA",
      details: [{ field: "name", message: "Required" }],
    });
    expect(notifyAppError).not.toHaveBeenCalled();
  });

  it("không phát toast trùng cho cùng một ApiError", () => {
    const error = createError("PROJECT_NOT_FOUND", "not-found", 404);
    handleApiError(error);
    handleApiError(error);
    expect(notifyAppError).toHaveBeenCalledOnce();
  });

  it("tôn trọng shouldNotify false của request", () => {
    handleApiError({ code: 500 }, { shouldNotify: false });
    expect(notifyAppError).not.toHaveBeenCalled();
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
