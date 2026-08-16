import type {
  CreateProjectRequest,
  ProjectResponse,
  ProjectSummaryResponse,
} from "@/api";
import { apiClient, createProject, deleteProject, listProjects } from "@/api";
import { requireApiData } from "@/common/api/require-api-data";

/** Tải danh sách Project bằng generated SDK và shared client.
 * @returns Các Project mà actor hiện tại được phép truy cập.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestProjects(): Promise<ProjectSummaryResponse[]> {
  const response = await listProjects({
    client: apiClient,
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Tạo Project từ contract được sinh trực tiếp bởi OpenAPI.
 * @param body Thông tin Project theo generated request type.
 * @returns Project vừa được tạo.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestProjectCreation(
  body: CreateProjectRequest,
): Promise<ProjectResponse> {
  const response = await createProject({
    body,
    client: apiClient,
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Xóa Project qua operation có operationId ổn định.
 * @param projectId ID Project cần xóa.
 * @returns Promise hoàn tất khi Backend đã xóa Project.
 * @throws ApiError khi request thất bại.
 */
export async function requestProjectDeletion(projectId: string): Promise<void> {
  await deleteProject({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
}
