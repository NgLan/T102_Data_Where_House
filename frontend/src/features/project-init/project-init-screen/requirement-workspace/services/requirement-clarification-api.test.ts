import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  deleteRequirement,
  sendProjectRequirementClarificationMessage,
} from "@/api";
import {
  requestRequirementDelete,
  requestRequirementMessage,
} from "./requirement-clarification-api";

vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: {},
  deleteRequirement: vi.fn(),
  sendProjectRequirementClarificationMessage: vi.fn(),
}));

describe("requirement clarification commands", () => {
  beforeEach(() => vi.clearAllMocks());

  it("sends a follow-up message with the current revision", async () => {
    vi.mocked(sendProjectRequirementClarificationMessage).mockResolvedValue({
      data: { data: { status: "READY" } },
    } as never);
    await requestRequirementMessage("project-1", "session-1", 4, "Refine it");
    expect(sendProjectRequirementClarificationMessage).toHaveBeenCalledWith(
      expect.objectContaining({ body: { expected_revision: 4, message: "Refine it" } }),
    );
  });

  it("deletes one structured requirement", async () => {
    vi.mocked(deleteRequirement).mockResolvedValue({} as never);
    await requestRequirementDelete("project-1", "requirement-1");
    expect(deleteRequirement).toHaveBeenCalledWith(expect.objectContaining({
      path: { project_id: "project-1", requirement_id: "requirement-1" },
    }));
  });
});
