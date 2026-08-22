import {
  apiClient,
  getCurrentActor,
  listProjects,
  requireApiData,
  type CurrentActorResponse,
  type ProjectSummaryResponse,
} from "@/api";

/** Tải các Project mà actor hiện tại được phép truy cập.
 * @returns Danh sách Project dùng chung cho header và màn quản lý.
 * @throws ApiError khi request thất bại; Error khi envelope thiếu payload.
 */
export async function getAccessibleProjects(): Promise<ProjectSummaryResponse[]> {
  const response = await listProjects({
    client: apiClient,
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Tải hồ sơ actor MVP hiện tại.
 * @returns ID, username và email của actor.
 * @throws ApiError khi request thất bại; Error khi envelope thiếu payload.
 */
export async function getCurrentActorProfile(): Promise<CurrentActorResponse> {
  const response = await getCurrentActor({
    client: apiClient,
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}
