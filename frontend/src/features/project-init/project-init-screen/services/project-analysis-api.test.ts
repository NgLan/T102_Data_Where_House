import { beforeEach, describe, expect, it, vi } from "vitest";
import { getProjectAnalysisStatus, reanalyzeProject, recheckProjectSourceCoverage, resolveProjectSourceCoverage, runProjectInitializationWorkflow } from "@/api";
import { analyzeProject, getAnalysisStatus, initializeProject, recheckSourceCoverage, resolveSourceCoverage } from "./project-analysis-api";

vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: {},
  getProjectAnalysisStatus: vi.fn(),
  reanalyzeProject: vi.fn(),
  recheckProjectSourceCoverage: vi.fn(),
  resolveProjectSourceCoverage: vi.fn(),
  runProjectInitializationWorkflow: vi.fn(),
}));

describe("project workflow adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("reanalyzes source and analytical requirements without generating a model", async () => {
    const status = { readiness_status: "SOURCE_DATA_REQUIRED", source_coverage_batch: null };
    vi.mocked(reanalyzeProject).mockResolvedValue({ data: { data: status } } as never);

    await expect(analyzeProject("project-1")).resolves.toEqual(status);

    expect(reanalyzeProject).toHaveBeenCalledOnce();
  });

  it("reads analysis status", async () => {
    const status = {
      requirement_analysis_outdated: false,
      source_analysis_outdated: false,
    };
    vi.mocked(getProjectAnalysisStatus).mockResolvedValue({
      data: { data: status },
    } as never);

    await expect(getAnalysisStatus("project-1")).resolves.toEqual(status);
  });

  it("runs the single Project Init workflow entry point", async () => {
    const output = { status: "COMPLETED", data_model_id: "model-1" };
    vi.mocked(runProjectInitializationWorkflow).mockResolvedValue({
      data: { data: output },
    } as never);
    await expect(initializeProject("project-1")).resolves.toEqual(output);
  });

  it("sends optimistic structured source confirmation", async () => {
    const status = { readiness_status: "SOURCE_CONFIRMATION_REQUIRED", source_coverage_batch: {} };
    vi.mocked(resolveProjectSourceCoverage).mockResolvedValue({
      data: { data: status },
    } as never);
    await expect(resolveSourceCoverage(
      "project-1", "assessment-1", "batch-1", 4, 2,
      "CONFIRM_CANDIDATE", "candidate-1",
    )).resolves.toEqual(status);
    expect(resolveProjectSourceCoverage).toHaveBeenCalledWith(expect.objectContaining({
      body: {
        batch_id: "batch-1", expected_source_revision: 4,
        expected_resolution_revision: 2, action: "CONFIRM_CANDIDATE",
        candidate_id: "candidate-1",
      },
    }));
  });

  it("rechecks one completed batch explicitly", async () => {
    const status = { readiness_status: "READY_FOR_DESIGN", source_coverage_batch: null };
    vi.mocked(recheckProjectSourceCoverage).mockResolvedValue({
      data: { data: status },
    } as never);
    await expect(recheckSourceCoverage("project-1", "batch-1", 5)).resolves.toEqual(status);
    expect(recheckProjectSourceCoverage).toHaveBeenCalledWith(expect.objectContaining({
      body: { batch_id: "batch-1", expected_source_revision: 5 },
    }));
  });
});
