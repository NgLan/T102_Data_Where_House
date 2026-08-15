/**
 * API Service thực thi DDL script lên Sandbox Database & tạo dữ liệu test
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { SandboxExecutionResponseDto } from '@/api/model/sandbox.dto';
import { ApiResponse } from '@/api/model/common-response.dto';

/**
 * Gửi thực thi DDL lên Sandbox Database
 */
export async function executeSandboxDdlApi(ddl: string, host: string): Promise<SandboxExecutionResponseDto> {
  const response: ApiResponse<SandboxExecutionResponseDto> = await apiClient.post(API_ENDPOINTS.EXECUTE_SANDBOX, {
    ddl,
    host,
  });
  return response.data;
}

/**
 * Sinh dữ liệu mẫu thử nghiệm (Mock Data)
 */
export async function generateTestDataApi(rowsCount: number = 100): Promise<SandboxExecutionResponseDto> {
  const response: ApiResponse<SandboxExecutionResponseDto> = await apiClient.post(API_ENDPOINTS.SIMULATE_TEST_DATA, {
    rows_count: rowsCount,
  });
  return response.data;
}
