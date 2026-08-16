import type { DataModelResponse, UpdateDataModelRequest } from "@/api";
import { apiClient, getDataModel, updateDataModel } from "@/api";
import { requireApiData } from "@/common/api/require-api-data";

/** Tải snapshot Data Model hiện tại bằng generated SDK.
 * @param projectId ID Project sở hữu Data Model.
 * @returns Snapshot Data Model hiện hành.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestDataModel(
  projectId: string,
): Promise<DataModelResponse> {
  const response = await getDataModel({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Lưu toàn bộ DBML với optimistic revision bằng generated SDK.
 * @param projectId ID Project sở hữu Data Model.
 * @param snapshot Snapshot hiện hành dùng làm optimistic base revision.
 * @param dbml DBML draft cần lưu.
 * @returns Snapshot Data Model sau cập nhật.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestDataModelUpdate(
  projectId: string,
  snapshot: DataModelResponse,
  dbml: string,
): Promise<DataModelResponse> {
  const body = createUpdateBody(snapshot, dbml);
  const response = await updateDataModel({
    body,
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Tạo payload update từ snapshot hiện hành và DBML draft. */
function createUpdateBody(
  snapshot: DataModelResponse,
  dbml: string,
): UpdateDataModelRequest {
  return {
    data_model_id: snapshot.id,
    dbml,
    base_revision: snapshot.revision,
  };
}
