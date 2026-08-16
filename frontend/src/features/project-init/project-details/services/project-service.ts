import type { ProjectResponse, UpdateProjectRequest } from "@/api";
import {
  apiClient,
  getProject as getProjectRequest,
  updateProject as updateProjectRequest,
} from "@/api";
import { requireApiData } from "@/common/api/require-api-data";

/** Lấy dự án hiện tại qua generated SDK.
 * @param projectId ID Project cần đọc.
 * @returns Payload chi tiết Project.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function getProjectDetails(
  projectId: string,
): Promise<ProjectResponse> {
  const response = await getProjectRequest({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Lưu thông tin Project; Data Source được quản lý qua API riêng.
 * @param projectId ID Project cần cập nhật.
 * @param form Thông tin Project đã được form schema xác thực.
 * @returns Payload Project sau cập nhật.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function updateProjectDetails(
  projectId: string,
  form: { name: string; domain: string; requirement: string },
): Promise<ProjectResponse> {
  const body: UpdateProjectRequest = {
    ...form,
    description: form.requirement,
  };
  const response = await updateProjectRequest({
    body,
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}
