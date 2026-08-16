/**
 * API Service thực thi DDL script lên Sandbox Database & quản lý cấu hình Sandbox DB
 */

import { apiClient } from '@/api/http/client';
import { ApiResponse } from '@/api/model/common-response.dto';
import type {
  DataModelDdlResponseDto,
  SandboxConfigRequestDto,
  SandboxConfigResponseDto,
  SandboxExecutionResponseDto,
  TestConnectionRequestDto,
  TestConnectionResponseDto,
} from '@/api/model/sandbox.dto';

/**
 * Lấy cấu hình Sandbox DB của dự án
 */
export async function getSandboxConfigApi(projectId: string): Promise<SandboxConfigResponseDto | null> {
  const response: ApiResponse<SandboxConfigResponseDto | null> = await apiClient.get(
    `/projects/${projectId}/sandbox/config`
  );
  return response.data;
}

/** Sinh DDL PostgreSQL từ revision Data Model hiện tại. */
export async function getDataModelDdlApi(projectId: string): Promise<DataModelDdlResponseDto> {
  const response: ApiResponse<DataModelDdlResponseDto> = await apiClient.get(
    `/projects/${projectId}/data-model/ddl`,
    { params: { dialect: 'postgresql' } }
  );
  return response.data;
}

/**
 * Lưu hoặc cập nhật cấu hình Sandbox DB cho dự án
 */
export async function saveSandboxConfigApi(
  projectId: string,
  config: SandboxConfigRequestDto
): Promise<SandboxConfigResponseDto> {
  const response: ApiResponse<SandboxConfigResponseDto> = await apiClient.post(
    `/projects/${projectId}/sandbox/config`,
    config
  );
  return response.data;
}

/**
 * Kiểm tra thử kết nối DB Sandbox
 */
export async function testSandboxConnectionApi(
  request: TestConnectionRequestDto
): Promise<TestConnectionResponseDto> {
  const response: ApiResponse<TestConnectionResponseDto> = await apiClient.post(
    '/sandbox/test-connection',
    request
  );
  return response.data;
}

/**
 * Gửi thực thi DDL script lên Sandbox Database
 */
export async function executeSandboxDdlApi(
  projectId: string,
  ddlScript: string
): Promise<SandboxExecutionResponseDto> {
  const response: ApiResponse<SandboxExecutionResponseDto> = await apiClient.post(
    `/projects/${projectId}/sandbox/execute-ddl`,
    { ddl_script: ddlScript }
  );
  return response.data;
}
