import type { DataModelResponse } from "@/api";
import {
  apiClient,
  generateDataModel,
  regenerateDataModel,
  requireApiData,
} from "@/api";

/** Chạy workflow tuần tự để tạo Data Model đầu tiên.
 *
 * @param projectId ID Project sở hữu nguồn dữ liệu và yêu cầu nghiệp vụ.
 * @returns Snapshot Data Model vừa được sinh và lưu xuống CSDL.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestDataModelGeneration(
  projectId: string,
): Promise<DataModelResponse> {
  const response = await generateDataModel({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Tạo lại Data Model từ input đã phân tích và ghi đè snapshot hiện hành. */
export async function requestDataModelRegeneration(
  projectId: string,
): Promise<DataModelResponse> {
  const response = await regenerateDataModel({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}
