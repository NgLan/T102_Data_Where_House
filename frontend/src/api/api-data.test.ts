import { describe, expect, it } from "vitest";
import { requireApiData, unwrapApiData } from "./api-data";

describe("api-data helpers", () => {
  it("unwrapApiData trả payload khi có dữ liệu và null khi rỗng", () => {
    expect(unwrapApiData({ data: { id: "p1" } })).toEqual({ id: "p1" });
    expect(unwrapApiData({ data: null })).toBeNull();
    expect(unwrapApiData({})).toBeNull();
  });

  it("requireApiData ném error khi backend không trả payload data", () => {
    expect(requireApiData({ data: "ok" })).toBe("ok");
    expect(() => requireApiData({ data: null })).toThrow("INVALID_API_RESPONSE");
  });
});
