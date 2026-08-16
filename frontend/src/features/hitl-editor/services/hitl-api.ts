/**
 * API Service thực thi AI Re-prompting & duyệt Proposal trong HITL Editor
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { ApiResponse } from '@/api/model/common-response.dto';
import { DataModelResponseDto } from '@/api/model/data-model.dto';
import {
  ChangeProposalDetailDto,
  ChangeProposalSummaryDto,
  ProposalStatus,
} from '../types/hitl.types';

/**
 * Nhờ AI Agent chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên (UC6 / T-024).
 * Kết quả là một đề xuất mới ở trạng thái PROPOSED, kèm DBML hiện hành để vẽ diff ngay.
 */
export async function reviseDataModelWithAiApi(
  dataModelId: string,
  instruction: string
): Promise<ChangeProposalDetailDto> {
  const response: ApiResponse<ChangeProposalDetailDto> = await apiClient.post(
    API_ENDPOINTS.AI_REVISE_DATA_MODEL(dataModelId),
    { instruction }
  );
  return response.data;
}

/**
 * Liệt kê các đề xuất thay đổi của một mô hình dữ liệu (mới nhất trước)
 */
export async function listChangeProposalsApi(
  dataModelId: string,
  status?: ProposalStatus
): Promise<ChangeProposalSummaryDto[]> {
  const response: ApiResponse<ChangeProposalSummaryDto[]> = await apiClient.get(
    API_ENDPOINTS.DATA_MODEL_CHANGES(dataModelId),
    { params: status ? { status } : undefined }
  );
  return response.data;
}

/**
 * Lấy chi tiết một đề xuất thay đổi kèm DBML hiện hành để dựng khung so sánh (UC6.1)
 */
export async function getChangeProposalApi(changeId: string): Promise<ChangeProposalDetailDto> {
  const response: ApiResponse<ChangeProposalDetailDto> = await apiClient.get(
    API_ENDPOINTS.CHANGE_PROPOSAL(changeId)
  );
  return response.data;
}

/**
 * Chấp nhận đề xuất và áp dụng vào mô hình dữ liệu (UC6.2 / T-032).
 * Trả về mô hình dữ liệu SAU khi áp dụng, đã mang revision mới.
 */
export async function acceptProposalApi(changeId: string): Promise<DataModelResponseDto> {
  const response: ApiResponse<DataModelResponseDto> = await apiClient.post(
    API_ENDPOINTS.ACCEPT_CHANGE_PROPOSAL(changeId)
  );
  return response.data;
}

/**
 * Từ chối một đề xuất thay đổi (UC6.3 / T-033).
 * Mô hình dữ liệu và revision giữ nguyên, chỉ trạng thái đề xuất đổi thành REJECTED.
 */
export async function rejectProposalApi(changeId: string): Promise<ChangeProposalSummaryDto> {
  const response: ApiResponse<ChangeProposalSummaryDto> = await apiClient.post(
    API_ENDPOINTS.REJECT_CHANGE_PROPOSAL(changeId)
  );
  return response.data;
}
