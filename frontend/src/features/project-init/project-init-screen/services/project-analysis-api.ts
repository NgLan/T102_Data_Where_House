import {
  type AnalysisStatusResponse,
  apiClient,
  getProjectAnalysisStatus,
  generateDataModel,
  handleApiError,
  reanalyzeProject,
  requireApiData,
} from "@/api";

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

/** Phân tích Requirement và source đã thay đổi, không generate Data Model. */
export type ProjectAnalysisAction = "generated" | "reanalyzed";

/** Phân tích lại hoặc sinh snapshot đầu tiên tùy trạng thái hiện hành. */
export async function analyzeProject(
  projectId: string,
): Promise<ProjectAnalysisAction> {
  const status = await getAnalysisStatus(projectId);
  if (!status.data_model_exists) {
    try {
      await generateDataModel({
        client: apiClient,
        path: { project_id: projectId },
        responseStyle: "fields",
        throwOnError: true,
      });
    } catch (error: unknown) {
      const normalized = handleApiError(error, { shouldNotify: false });
      if (normalized.errorCode !== "DATA_MODEL_ALREADY_EXISTS") throw error;
      const latestStatus = await getAnalysisStatus(projectId);
      if (!latestStatus.data_model_exists) throw error;
    }
    return "generated";
  }
  await reanalyzeProject({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return "reanalyzed";
}
