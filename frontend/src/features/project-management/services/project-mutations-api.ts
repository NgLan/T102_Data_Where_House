import {
  apiClient,
  createProject as createProjectRequest,
  deleteProject as deleteProjectRequest,
  requireApiData,
  type CreateProjectRequest,
  type ProjectResponse,
} from "@/api";

/** Tạo Project bằng generated SDK.
 * @param body Payload đã được form schema chuẩn hóa.
 * @returns Project vừa được tạo.
 * @throws ApiError khi request thất bại; Error khi envelope thiếu payload.
 */
export async function createProject(body: CreateProjectRequest): Promise<ProjectResponse> {
  const response = await createProjectRequest({
    body, client: apiClient, responseStyle: "fields", throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Xóa Project bằng generated SDK.
 * @param projectId ID Project cần xóa.
 * @returns Promise hoàn tất sau response 204.
 * @throws ApiError khi request thất bại.
 */
export async function deleteProject(projectId: string): Promise<void> {
  await deleteProjectRequest({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
}
