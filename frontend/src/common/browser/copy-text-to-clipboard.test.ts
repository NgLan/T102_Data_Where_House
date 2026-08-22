// @vitest-environment jsdom

import { beforeEach, describe, expect, it, vi } from "vitest";
import { copyTextToClipboard } from "./copy-text-to-clipboard";

const writeText = vi.fn();

describe("copyTextToClipboard", () => {
  beforeEach(() => {
    writeText.mockReset();
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
  });

  it("trả true khi browser sao chép thành công", async () => {
    writeText.mockResolvedValue(undefined);
    await expect(copyTextToClipboard("DDL")).resolves.toBe(true);
    expect(writeText).toHaveBeenCalledWith("DDL");
  });

  it("trả false khi browser từ chối clipboard", async () => {
    writeText.mockRejectedValue(new DOMException("Denied"));
    await expect(copyTextToClipboard("DDL")).resolves.toBe(false);
  });
});
