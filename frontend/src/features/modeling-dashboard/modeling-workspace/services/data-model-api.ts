import type { DataModelResponse, UpdateDataModelRequest } from "@/api";
import { apiClient, getDataModel, updateDataModel } from "@/api";

/** Tải snapshot Data Model hiện tại bằng generated SDK. */
export async function requestDataModel(
  projectId: string,
): Promise<DataModelResponse> {
  const response = await getDataModel({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "data",
    throwOnError: true,
  });
  return requireSnapshot(response.data.data);
}

/** Lưu toàn bộ DBML với optimistic revision bằng generated SDK. */
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
    responseStyle: "data",
    throwOnError: true,
  });
  return requireSnapshot(response.data.data);
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

/** Bảo đảm success envelope chứa snapshot bắt buộc. */
function requireSnapshot(
  value: DataModelResponse | null | undefined,
): DataModelResponse {
  if (!value) throw new Error("INVALID_DBML_CONTENT");
  return value;
}
