import { beforeEach, describe, expect, it, vi } from "vitest";
const { extractRawText } = vi.hoisted(() => ({ extractRawText: vi.fn() }));
vi.mock("mammoth", () => ({ default: { extractRawText } }));
import { parseRequirementDocument } from "./requirement-document-parser";

describe("parseRequirementDocument", () => {
  beforeEach(() => extractRawText.mockReset());
  it.each([["requirements.txt", " text "], ["requirements.md", " # title "]])("reads %s with File API", async (name, content) => {
    await expect(parseRequirementDocument(new File([content], name))).resolves.toBe(content.trim());
    expect(extractRawText).not.toHaveBeenCalled();
  });
  it("reads DOCX with Mammoth", async () => {
    extractRawText.mockResolvedValue({ value: " requirement " });
    await expect(parseRequirementDocument(new File(["x"], "r.docx"))).resolves.toBe("requirement");
  });
});
