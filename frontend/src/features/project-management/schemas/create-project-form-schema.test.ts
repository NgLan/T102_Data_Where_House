import { describe, expect, it } from "vitest";
import {
  MAX_PROJECT_DOMAIN_LENGTH,
  MAX_PROJECT_NAME_LENGTH,
  MIN_PROJECT_NAME_LENGTH,
  MIN_PROJECT_REQUIREMENT_LENGTH,
} from "@/common/constants/project-constraints";
import { createProjectFormSchema } from "./create-project-form-schema";

describe("createProjectFormSchema", () => {
  it("dùng chung Project constraints tại các biên hợp lệ", () => {
    const result = createProjectFormSchema.safeParse({
      name: "P".repeat(MIN_PROJECT_NAME_LENGTH),
      domain: "d".repeat(MAX_PROJECT_DOMAIN_LENGTH),
      requirement: "r".repeat(MIN_PROJECT_REQUIREMENT_LENGTH),
    });
    expect(result.success).toBe(true);
  });

  it("từ chối giá trị vượt Project constraints", () => {
    const result = createProjectFormSchema.safeParse({
      name: "P".repeat(MAX_PROJECT_NAME_LENGTH + 1),
      domain: "d".repeat(MAX_PROJECT_DOMAIN_LENGTH + 1),
      requirement: "short",
    });
    expect(result.success).toBe(false);
    expect(result.error?.issues.map((issue) => issue.message)).toEqual([
      "ERROR_NAME_MAX",
      "ERROR_DOMAIN_MAX",
      "ERROR_REQUIREMENT_MIN",
    ]);
  });
});
