import type {
  CreateProjectRequest,
  ProjectResponse,
  RawRequirementResponse,
  UpdateProjectRequest,
} from "@/api";
import {
  apiClient,
  getProject as getProjectRequest,
  requireApiData,
  saveProjectRawRequirement,
  updateProject as updateProjectRequest,
} from "@/api";

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
  form: Pick<CreateProjectRequest, "name" | "domain" | "description">,
): Promise<ProjectResponse> {
  const body: UpdateProjectRequest = {
    name: form.name,
    domain: form.domain ?? null,
    description: form.description ?? null,
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

/** Lưu riêng Raw Requirement bằng expected revision. */
export async function saveRawRequirement(
  projectId: string,
  requirement: string,
  expectedRevision: number,
): Promise<RawRequirementResponse> {
  const response = await saveProjectRawRequirement({
    body: {
      requirement: requirement.trim() || null,
      expected_revision: expectedRevision,
    },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}
