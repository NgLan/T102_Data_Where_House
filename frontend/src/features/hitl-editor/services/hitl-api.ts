/**
 * API Service thực thi AI Re-prompting & duyệt Proposal trong HITL Editor
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { ApiResponse } from '@/api/model/common-response.dto';
import {
  ChangeProposalDetailDto,
  ChangeProposalSummaryDto,
  ProposalStatus,
} from '../types/hitl.types';

export interface RepromptResponseDto {
  ai_response: string;
  proposed_attributes?: Array<{
    name: string;
    dataType: string;
    keyType: 'PK' | 'FK' | 'NONE';
    isNullable: boolean;
  }>;
}

/**
 * Gửi câu hỏi re-prompting cho AI Agent sửa bảng
 */
export async function sendRepromptMessageApi(tableName: string, prompt: string): Promise<RepromptResponseDto> {
  const response: ApiResponse<RepromptResponseDto> = await apiClient.post(API_ENDPOINTS.REPROMPT_HITL, {
    table_name: tableName,
    prompt,
  });
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
 * Chấp nhận đề xuất Proposal thay đổi
 */
export async function acceptProposalApi(proposalId: string): Promise<boolean> {
  const response: ApiResponse<{ success: boolean }> = await apiClient.post(API_ENDPOINTS.ACCEPT_PROPOSAL, {
    proposal_id: proposalId,
  });
  return response.data.success;
}
