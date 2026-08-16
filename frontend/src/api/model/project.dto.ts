/**
 * Định nghĩa các DTO liên quan đến Khởi tạo Dự án & Dữ liệu Nguồn Excel
 */

/**
 * Payload khởi tạo dự án
 */
export interface CreateProjectRequestDto {
  domain: string;
  target_dialect: string;
  business_description: string;
  is_masking_enabled: boolean;
}

/**
 * Phản hồi khởi tạo dự án
 */
export interface ProjectResponseDto {
  project_id: string;
  domain: string;
  target_dialect: string;
  status: string;
  created_at: string;
}

/**
 * Cấu trúc dữ liệu hàng xem trước từ Excel
 */
export interface ExcelPreviewRowDto {
  stt: number;
  ride_id: string;
  driver_id: string;
  customer_id: string;
  fare_amount: number;
  status: string;
  created_at: string;
}

/**
 * Phản hồi xem trước file Excel
 */
export interface ExcelPreviewResponseDto {
  sheet_name: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  rows: ExcelPreviewRowDto[];
}
