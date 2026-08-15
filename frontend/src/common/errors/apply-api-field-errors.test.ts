import { describe, expect, it, vi } from "vitest";
import { ApiError } from "./api-error";
import { applyApiFieldErrors } from "./apply-api-field-errors";

describe("applyApiFieldErrors", () => {
  it("map table_name vào setError tương thích React Hook Form", () => {
    const setError = vi.fn();
    const error = new ApiError({
      status: 422,
      errorCode: "INVALID_INPUT_SCHEMA",
      message: "Invalid",
      details: [{ field: "table_name", message: "Already exists" }],
      kind: "validation",
      originalError: null,
    });
    const result = applyApiFieldErrors(error, {
      setError,
      resolveField: (field) => (field === "table_name" ? field : null),
    });
    expect(setError).toHaveBeenCalledWith("table_name", {
      type: "server",
      message: "Already exists",
    });
    expect(result.unmapped).toEqual([]);
  });
});
