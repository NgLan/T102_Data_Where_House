/**
 * API Service sinh mã DDL từ mô hình dữ liệu, thực thi DDL lên Sandbox & tạo dữ liệu test
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { SandboxExecutionResponseDto } from '@/api/model/sandbox.dto';
import { ApiResponse } from '@/api/model/common-response.dto';
import { DdlGenerationResponseDto, SqlDialect } from '../types/sandbox.types';

/**
 * Sinh mã DDL từ mô hình dữ liệu theo hệ quản trị CSDL người dùng đã chọn (UC5.4 / UC5.5)
 */
export async function generateDdlApi(
  dataModelId: string,
  dialect: SqlDialect
): Promise<DdlGenerationResponseDto> {
  const response: ApiResponse<DdlGenerationResponseDto> = await apiClient.get(
    API_ENDPOINTS.DATA_MODEL_DDL(dataModelId),
    { params: { dialect } }
  );
  return response.data;
}

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
