import type {
  DataSourceListResponse,
  DataSourcePreviewResponse,
  UploadDataSourcesResponse,
} from "@/api";
import {
  apiClient,
  deleteProjectDataSource,
  getProjectDataSourcePreview,
  listProjectDataSources,
  requireApiData,
  uploadProjectDataSources,
} from "@/api";

/** Liệt kê source và quyền chỉnh sửa của actor hiện tại.
 * @param projectId ID Project sở hữu Data Source.
 * @returns Danh sách source cùng quyền chỉnh sửa.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function listDataSources(
  projectId: string,
): Promise<DataSourceListResponse> {
  const response = await listProjectDataSources({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Upload batch CSV qua multipart generated SDK.
 * @param projectId ID Project nhận các tệp tải lên.
 * @param files Danh sách tệp CSV đã qua validation phía client.
 * @returns Kết quả profiling Data Source.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function uploadDataSources(
  projectId: string,
  files: File[],
): Promise<UploadDataSourcesResponse> {
  const response = await uploadProjectDataSources({
    body: { files },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Đọc preview CSV theo yêu cầu.
 * @param projectId ID Project sở hữu Data Source.
 * @param sourceId ID Data Source cần xem trước.
 * @returns Metadata và các dòng preview.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function getDataSourcePreview(
  projectId: string,
  sourceId: string,
): Promise<DataSourcePreviewResponse> {
  const response = await getProjectDataSourcePreview({
    client: apiClient,
    path: { project_id: projectId, source_id: sourceId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Xóa source qua generated SDK.
 * @param projectId ID Project sở hữu Data Source.
 * @param sourceId ID Data Source cần xóa.
 * @returns Promise hoàn tất khi Backend đã xóa source.
 * @throws ApiError khi request thất bại.
 */
export async function deleteDataSource(
  projectId: string,
  sourceId: string,
): Promise<void> {
  await deleteProjectDataSource({
    client: apiClient,
    path: { project_id: projectId, source_id: sourceId },
    responseStyle: "fields",
    throwOnError: true,
  });
}
