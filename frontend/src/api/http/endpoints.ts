/** Endpoint legacy chỉ dành cho các operation chưa có trong generated SDK. */

export const API_ENDPOINTS = {
  // Endpoints khởi tạo & dữ liệu nguồn
  PROJECT_INIT: '/projects/init',
  UPLOAD_DATA_SOURCE: '/projects/upload-datasource',

  // Endpoints mô hình hóa & AI Agent ERD
  GENERATE_ERD: '/modeling/generate-erd',
  UPDATE_DBML: '/modeling/update-dbml',
  GET_INSIGHTS: '/modeling/insights',

  // Endpoints Mô hình Dữ liệu (Data Model) — UC5.4, UC5.5
  /** Lấy mô hình dữ liệu hiện hành của một dự án */
  DATA_MODEL_BY_PROJECT: (projectId: string): string =>
    `/projects/${projectId}/data-model`,
  /** Sinh mã DDL từ mô hình dữ liệu theo hệ quản trị CSDL đã chọn */
  DATA_MODEL_DDL: (dataModelId: string): string =>
    `/data-models/${dataModelId}/ddl`,

  // Endpoints Đề xuất Thay đổi (Proposal Review) — UC6.1, UC6.2, UC6.3
  /** Liệt kê đề xuất thay đổi của một mô hình dữ liệu */
  DATA_MODEL_CHANGES: (dataModelId: string): string =>
    `/data-models/${dataModelId}/changes`,
  /** Xem chi tiết một đề xuất thay đổi (kèm DBML hiện hành để so sánh) */
  CHANGE_PROPOSAL: (changeId: string): string =>
    `/data-model-changes/${changeId}`,
  /** Nhờ AI Agent chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên */
  AI_REVISE_DATA_MODEL: (dataModelId: string): string =>
    `/data-models/${dataModelId}/ai-revisions`,
  /** Chấp nhận đề xuất và áp dụng vào mô hình dữ liệu hiện tại */
  ACCEPT_CHANGE_PROPOSAL: (changeId: string): string =>
    `/data-model-changes/${changeId}/accept`,
  /** Từ chối một đề xuất thay đổi */
  REJECT_CHANGE_PROPOSAL: (changeId: string): string =>
    `/data-model-changes/${changeId}/reject`,
<<<<<<< HEAD

  // Endpoints HITL Editor
  REPROMPT_HITL: '/hitl/reprompt',
=======
>>>>>>> ab3fdf5 (feat(data-model): add PII guard)

  // Endpoints DDL Sandbox
  EXECUTE_SANDBOX: '/sandbox/execute',
  SIMULATE_TEST_DATA: '/sandbox/simulate-data',
} as const;
