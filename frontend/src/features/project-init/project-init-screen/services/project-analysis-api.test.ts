import { beforeEach, describe, expect, it, vi } from "vitest";
import { generateDataModel, getProjectAnalysisStatus, reanalyzeProject } from "@/api";
import { analyzeProject, getAnalysisStatus } from "./project-analysis-api";

vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()), apiClient: {},
  generateDataModel: vi.fn(), getProjectAnalysisStatus: vi.fn(), reanalyzeProject: vi.fn(),
}));

describe("project workflow adapter", () => {
  beforeEach(() => vi.clearAllMocks());
  it("reanalyzes when the project already has a model", async () => {
    vi.mocked(getProjectAnalysisStatus).mockResolvedValue({ data: { data: { data_model_exists: true } } } as never);
    vi.mocked(reanalyzeProject).mockResolvedValue({ data: undefined } as never);
    await expect(analyzeProject("project-1")).resolves.toBe("reanalyzed");
    expect(reanalyzeProject).toHaveBeenCalledOnce();
    expect(generateDataModel).not.toHaveBeenCalled();
  });
  it("generates the first model instead of reanalyzing twice", async () => {
    vi.mocked(getProjectAnalysisStatus).mockResolvedValue({ data: { data: { data_model_exists: false } } } as never);
    vi.mocked(generateDataModel).mockResolvedValue({ data: undefined } as never);
    await expect(analyzeProject("project-1")).resolves.toBe("generated");
    expect(generateDataModel).toHaveBeenCalledOnce();
    expect(reanalyzeProject).not.toHaveBeenCalled();
  });
  it("accepts a model generated concurrently in another tab", async () => {
    vi.mocked(getProjectAnalysisStatus)
      .mockResolvedValueOnce({ data: { data: { data_model_exists: false } } } as never)
      .mockResolvedValueOnce({ data: { data: { data_model_exists: true } } } as never);
    vi.mocked(generateDataModel).mockRejectedValueOnce({
      code: 409,
      error_code: "DATA_MODEL_ALREADY_EXISTS",
      message: "Already exists",
    });

    await expect(analyzeProject("project-1")).resolves.toBe("generated");
    expect(getProjectAnalysisStatus).toHaveBeenCalledTimes(2);
  });
  it("reads analysis status", async () => {
    const status = { requirement_analysis_outdated: false, source_analysis_outdated: false };
    vi.mocked(getProjectAnalysisStatus).mockResolvedValue({ data: { data: status } } as never);
    await expect(getAnalysisStatus("project-1")).resolves.toEqual(status);
  });
});
