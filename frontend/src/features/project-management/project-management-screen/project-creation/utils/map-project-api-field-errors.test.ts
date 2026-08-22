import { describe, expect, it, vi } from "vitest";
import type { ApiError } from "@/api";
import { CUSTOM_PROJECT_DOMAIN } from "@/common/projects/project-domain-options";
import { mapProjectApiFieldErrors } from "./map-project-api-field-errors";

function apiError(details: ApiError["details"]): ApiError {
  return { name: "ApiError", message: "Invalid", errorCode: "VALIDATION_ERROR", details } as ApiError;
}

describe("mapProjectApiFieldErrors", () => {
  it("map domain error vào customDomain khi custom đang được chọn", () => {
    const setError = vi.fn();
    const count = mapProjectApiFieldErrors(apiError([
      { field: "body.domain", message: "Too long" },
    ]), setError, CUSTOM_PROJECT_DOMAIN);
    expect(setError).toHaveBeenCalledWith("customDomain", {
      type: "server", message: "Too long",
    });
    expect(count).toBe(0);
  });

  it("trả số detail không thuộc form", () => {
    expect(mapProjectApiFieldErrors(apiError([
      { field: "body.unknown", message: "Unknown" },
    ]), vi.fn(), "ride")).toBe(1);
  });
});
