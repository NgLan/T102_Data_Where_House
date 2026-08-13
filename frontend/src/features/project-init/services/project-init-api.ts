/**
 * API Service thực thi các truy vấn khởi tạo Project & upload dữ liệu nguồn Excel
 */

import { apiClient } from '@/api/http/client';
import { API_ENDPOINTS } from '@/api/http/endpoints';
import { CreateProjectRequestDto, ProjectResponseDto, ExcelPreviewResponseDto } from '@/api/model/project.dto';
import { ApiResponse } from '@/api/model/common-response.dto';

/**
 * Khởi tạo một dự án Data Warehouse mới
 */
export async function createProjectApi(data: CreateProjectRequestDto): Promise<ProjectResponseDto> {
  const response: ApiResponse<ProjectResponseDto> = await apiClient.post(API_ENDPOINTS.PROJECT_INIT, data);
  return response.data;
}

/**
 * Tải file Excel nguồn và nhận xem trước dữ liệu
 */
export async function uploadExcelSourceApi(file: File): Promise<ExcelPreviewResponseDto> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response: ApiResponse<ExcelPreviewResponseDto> = await apiClient.post(
    API_ENDPOINTS.UPLOAD_DATA_SOURCE,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data;
}
