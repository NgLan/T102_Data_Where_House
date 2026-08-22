import type { DataModelResponse, UpdateDataModelRequest } from "@/api";
import { apiClient, getDataModel, requireApiData, updateDataModel } from "@/api";

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
    meta: { shouldNotify: false },
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

/** Tạo payload update từ snapshot hiện hành và DBML draft.
 *
 * Không có snapshot nghĩa là dự án chưa có Data Model — gửi mỗi `dbml` để Backend tạo
 * bản đầu tiên, vì lúc này chưa tồn tại revision nào để optimistic locking dựa vào.
 */
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
