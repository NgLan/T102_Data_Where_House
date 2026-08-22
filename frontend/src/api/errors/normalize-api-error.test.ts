import { describe, expect, it } from "vitest";
import { normalizeApiError } from "./normalize-api-error";

describe("normalizeApiError", () => {
  it("chuẩn hóa Backend ApiError và validation details", () => {
    const error = normalizeApiError({
      code: 400,
      message: "Invalid input",
      error_code: "INVALID_INPUT_SCHEMA",
      details: [{ field: "name", message: "Required" }],
    });
    expect(error).toMatchObject({
      status: 400,
      errorCode: "INVALID_INPUT_SCHEMA",
      kind: "validation",
      details: [{ field: "name", message: "Required" }],
    });
  });

  it("chuẩn hóa network error không có response", () => {
    const error = normalizeApiError(new TypeError("Failed to fetch"));
    expect(error).toMatchObject({
      status: null,
      errorCode: "NETWORK_ERROR",
      kind: "network",
    });
  });

  it("chuẩn hóa AbortError thành timeout", () => {
    const error = normalizeApiError(new DOMException("Aborted", "AbortError"));
    expect(error).toMatchObject({ errorCode: "TIMEOUT_ERROR", kind: "timeout" });
  });

  it.each([
    [403, "authorization"],
    [404, "not-found"],
    [409, "conflict"],
    [500, "system"],
  ] as const)("phân loại HTTP %s", (status, kind) => {
    expect(normalizeApiError({ code: status }, { status }).kind).toBe(kind);
  });

  it("ưu tiên error_code conflict ổn định", () => {
    const error = normalizeApiError({
      code: 400,
      message: "Conflict",
      error_code: "DATA_MODEL_REVISION_CONFLICT",
    });
    expect(error.kind).toBe("conflict");
  });

  it("giữ unknown error làm nguyên nhân gốc", () => {
    const original = new Error("unexpected value");
    const error = normalizeApiError(original);
    expect(error.kind).toBe("unknown");
    expect(error.errorCode).toBe("UNKNOWN_ERROR");
    expect(error.originalError).toBe(original);
  });
});
