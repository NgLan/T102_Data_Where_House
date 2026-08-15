/**
 * API Service thực thi đồng bộ DBML & lấy danh sách AI Insights
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { ErdGenerationResponseDto, InsightItemDto } from '@/api/model/erd.dto';
import { ApiResponse } from '@/api/model/common-response.dto';

/**
 * Gửi cập nhật DBML code để AI sinh lại sơ đồ ERD
 */
export async function updateDbmlApi(dbml: string): Promise<ErdGenerationResponseDto> {
  const response: ApiResponse<ErdGenerationResponseDto> = await apiClient.post(API_ENDPOINTS.UPDATE_DBML, { dbml });
  return response.data;
}

/**
 * Lấy danh sách cảnh báo AI Insights
 */
export async function fetchInsightsApi(): Promise<InsightItemDto[]> {
  const response: ApiResponse<InsightItemDto[]> = await apiClient.get(API_ENDPOINTS.GET_INSIGHTS);
  return response.data;
}
