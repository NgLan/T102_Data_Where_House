import { describe, expect, it } from "vitest";
import sandboxEn from "@/common/i18n/locales/en/sandbox-deployment.json";
import sandboxVi from "@/common/i18n/locales/vi/sandbox-deployment.json";

describe("sandbox deployment i18n", () => {
  it("giữ bộ translation key VI và EN đồng nhất", () => {
    expect(Object.keys(sandboxEn).sort()).toEqual(Object.keys(sandboxVi).sort());
  });
});
