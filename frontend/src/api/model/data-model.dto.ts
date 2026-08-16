/**
 * DTO dùng chung cho Mô hình Dữ liệu (Data Model).
 * Đặt tại src/api/model vì được dùng bởi nhiều feature (modeling-dashboard, hitl-editor,
 * sandbox-deployment) — theo quy tắc cấm gọi chéo giữa các feature.
 */

/** Payload backend trả về cho mô hình dữ liệu hiện hành của một dự án */
export interface DataModelResponseDto {
  id: string;
  project_id: string;
  dbml: string;
  revision: number;
  created_at: string;
  updated_at: string;
}
