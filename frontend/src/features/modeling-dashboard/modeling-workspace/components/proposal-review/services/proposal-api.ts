import type {
  ChangeProposalDetailResponse,
  ChangeProposalSummaryResponse,
  DataModelResponse,
} from "@/api";
import {
  acceptChangeProposal,
  apiClient,
  createAiDataModelProposal,
  getProjectDataModelChange,
  getPendingProjectDataModelChange,
  rejectChangeProposal,
  requireApiData,
  unwrapApiData,
} from "@/api";

/** Nhờ AI Agent chỉnh sửa mô hình và ghi thành đề xuất chờ duyệt (UC6.1).
 *
 * Mô hình trong `data_models` KHÔNG đổi cho tới khi người dùng chấp nhận đề xuất.
 *
 * @param projectId ID Project sở hữu Data Model.
 * @param instruction Yêu cầu chỉnh sửa viết bằng ngôn ngữ tự nhiên.
 * @returns Chi tiết đề xuất kèm DBML hiện hành để dựng khung so sánh.
 * @throws ApiError khi request thất bại; Error khi success envelope thiếu payload.
 */
export async function requestProposalFromAgent(
  projectId: string,
  instruction: string,
): Promise<ChangeProposalDetailResponse> {
  // `meta.shouldNotify` tắt toast toàn cục vì khung chat đã hiển thị lỗi ngay trong bong bóng.
  const response = await createAiDataModelProposal({
    body: { instruction },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Đọc chi tiết một đề xuất để dựng khung so sánh khác biệt.
 * @param projectId ID Project sở hữu Data Model.
 * @param changeId ID đề xuất cần xem.
 * @returns DBML đề xuất kèm DBML hiện hành và cờ lỗi thời.
 */
export async function fetchProposalDetail(
  projectId: string,
  changeId: string,
): Promise<ChangeProposalDetailResponse> {
  const response = await getProjectDataModelChange({
    client: apiClient,
    path: { project_id: projectId, change_id: changeId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

export async function fetchPendingProposal(
  projectId: string,
): Promise<ChangeProposalDetailResponse | null> {
  const response = await getPendingProjectDataModelChange({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return unwrapApiData(response.data);
}

/** Chấp nhận đề xuất và áp DBML vào mô hình chính thức (UC6.2).
 * @param changeId ID đề xuất cần áp dụng.
 * @returns Snapshot Data Model sau khi tăng revision.
 */
export async function acceptProposal(changeId: string): Promise<DataModelResponse> {
  const response = await acceptChangeProposal({
    client: apiClient,
    path: { change_id: changeId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Từ chối đề xuất; mô hình dữ liệu giữ nguyên (UC6.3).
 * @param changeId ID đề xuất cần từ chối.
 * @returns Bản tóm tắt đề xuất sau khi chuyển sang `REJECTED`.
 */
export async function rejectProposal(
  changeId: string,
): Promise<ChangeProposalSummaryResponse> {
  const response = await rejectChangeProposal({
    client: apiClient,
    path: { change_id: changeId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}
