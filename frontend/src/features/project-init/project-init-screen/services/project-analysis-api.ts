import {
  type AnalysisStatusResponse,
  apiClient,
  getProjectAnalysisStatus,
  getProjectSourceCoverage,
  recheckProjectSourceCoverage,
  resolveProjectSourceCoverage,
  runProjectInitializationWorkflow,
  reanalyzeProject,
  requireApiData,
} from "@/api";
import type { ProjectInitializationResponse } from "@/api";

/** Đọc trạng thái analysis hiện hành của Project. */
export async function getAnalysisStatus(
  projectId: string,
): Promise<AnalysisStatusResponse> {
  const response = await getProjectAnalysisStatus({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Reload persisted Source Coverage state independently from browser storage. */
export async function getSourceCoverage(
  projectId: string,
): Promise<AnalysisStatusResponse> {
  const response = await getProjectSourceCoverage({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Profile source và derive analytical output; tuyệt đối không sinh Data Model. */
export async function analyzeProject(
  projectId: string,
): Promise<AnalysisStatusResponse> {
  const response = await reanalyzeProject({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Persist one Source Confirmation item without invoking coverage analysis. */
export async function resolveSourceCoverage(
  projectId: string,
  assessmentId: string,
  batchId: string,
  expectedSourceRevision: number,
  expectedResolutionRevision: number,
  action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES",
  candidateId?: string,
): Promise<AnalysisStatusResponse> {
  const response = await resolveProjectSourceCoverage({
    client: apiClient,
    path: { project_id: projectId, assessment_id: assessmentId },
    body: {
      batch_id: batchId,
      expected_source_revision: expectedSourceRevision,
      expected_resolution_revision: expectedResolutionRevision,
      action,
      candidate_id: candidateId,
    },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Materialize a completed confirmation batch and rerun Source Coverage once. */
export async function recheckSourceCoverage(
  projectId: string,
  batchId: string,
  expectedSourceRevision: number,
): Promise<AnalysisStatusResponse> {
  const response = await recheckProjectSourceCoverage({
    client: apiClient,
    path: { project_id: projectId },
    body: { batch_id: batchId, expected_source_revision: expectedSourceRevision },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Chạy workflow Project Init đến clarification pause hoặc DBML hoàn tất. */
export async function initializeProject(
  projectId: string,
): Promise<ProjectInitializationResponse> {
  const response = await runProjectInitializationWorkflow({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}
