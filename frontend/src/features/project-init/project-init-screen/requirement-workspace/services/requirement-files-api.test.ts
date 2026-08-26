// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";
import { uploadProjectRequirementFiles } from "@/api";
import { requestRequirementFileUpload } from "./requirement-files-api";

vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: {},
  uploadProjectRequirementFiles: vi.fn(),
}));

describe("requirement files adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("sends every selected file and the latest revision as multipart fields", async () => {
    const files = [new File(["first"], "first.md"), new File(["second"], "second.txt")];
    vi.mocked(uploadProjectRequirementFiles).mockResolvedValue({
      data: { data: { items: [], requirement_revision: 5 } },
    } as never);
    await requestRequirementFileUpload("project-1", files, 4);
    expect(uploadProjectRequirementFiles).toHaveBeenCalledWith(expect.objectContaining({
      body: { files, expected_revision: 4 },
      path: { project_id: "project-1" },
    }));
  });
});
