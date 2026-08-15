/**
 * API Service thực thi AI Re-prompting & duyệt Proposal trong HITL Editor
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { ApiResponse } from '@/api/model/common-response.dto';

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
 * Chấp nhận đề xuất Proposal thay đổi
 */
export async function acceptProposalApi(proposalId: string): Promise<boolean> {
  const response: ApiResponse<{ success: boolean }> = await apiClient.post(API_ENDPOINTS.ACCEPT_PROPOSAL, {
    proposal_id: proposalId,
  });
  return response.data.success;
}
