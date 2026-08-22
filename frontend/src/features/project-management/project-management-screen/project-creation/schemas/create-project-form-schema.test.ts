import { describe, expect, it } from "vitest";
import { CUSTOM_PROJECT_DOMAIN } from "@/common/projects/project-domain-options";
import { createProjectFormSchema } from "./create-project-form-schema";

const VALID_FORM = {
  name: "Revenue Warehouse",
  domainSelection: "ride",
  customDomain: "",
  description: "Project description",
};

describe("createProjectFormSchema", () => {
  it("map predefined domain và không gửi requirement", () => {
    const result = createProjectFormSchema.parse(VALID_FORM);
    expect(result).toEqual({
      name: "Revenue Warehouse",
      domain: "ride",
      description: "Project description",
    });
    expect(result).not.toHaveProperty("requirement");
  });

  it("trim custom domain trước khi gửi", () => {
    const result = createProjectFormSchema.parse({
      ...VALID_FORM,
      domainSelection: CUSTOM_PROJECT_DOMAIN,
      customDomain: "  Insurance  ",
    });
    expect(result.domain).toBe("Insurance");
  });

  it("bắt buộc custom domain có nội dung", () => {
    const result = createProjectFormSchema.safeParse({
      ...VALID_FORM,
      domainSelection: CUSTOM_PROJECT_DOMAIN,
    });
    expect(result.error?.issues[0]).toMatchObject({
      path: ["customDomain"],
      message: "MSG_CUSTOM_DOMAIN_REQUIRED",
    });
  });

  it("giới hạn custom domain ở 100 ký tự", () => {
    const result = createProjectFormSchema.safeParse({
      ...VALID_FORM,
      domainSelection: CUSTOM_PROJECT_DOMAIN,
      customDomain: "a".repeat(101),
    });
    expect(result.error?.issues[0]).toMatchObject({
      path: ["customDomain"],
      message: "MSG_PROJECT_DOMAIN_MAX",
    });
  });

  it("chuẩn hóa description rỗng thành null", () => {
    const result = createProjectFormSchema.parse({ ...VALID_FORM, description: "   " });
    expect(result.description).toBeNull();
  });
});
