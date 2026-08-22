import type { DataModelValidationIssueResponse } from "@/api";
import { apiClient, requireApiData, validateDataModelDraft } from "@/api";

/** Kiểm tra DBML draft bằng Validation Engine của Backend. */
export async function requestDraftValidation(
  projectId: string,
  dbml: string,
): Promise<DataModelValidationIssueResponse[]> {
  const response = await validateDataModelDraft({
    body: { dbml },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}
