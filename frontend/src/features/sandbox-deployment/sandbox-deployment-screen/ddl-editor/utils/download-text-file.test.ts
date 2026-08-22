// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from "vitest";
import { downloadTextFile } from "./download-text-file";

describe("downloadTextFile", () => {
  afterEach(() => vi.restoreAllMocks());

  it("click link rồi remove và revoke Blob URL", () => {
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const createUrl = vi.fn(() => "blob:ddl");
    const revokeUrl = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createUrl });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeUrl });
    downloadTextFile({ filename: "schema.sql", content: "DDL", mimeType: "text/plain" });
    expect(click).toHaveBeenCalledOnce();
    expect(createUrl).toHaveBeenCalledOnce();
    expect(revokeUrl).toHaveBeenCalledWith("blob:ddl");
    expect(document.querySelector("a[download='schema.sql']")).toBeNull();
  });
});
