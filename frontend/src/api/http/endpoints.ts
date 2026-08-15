/**
 * Danh sách hằng số API Endpoints cho hệ thống Backend
 * Base URL đã bao gồm tiền tố /api/v1 (xem client.ts)
 */

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

  // Endpoints HITL Editor
  REPROMPT_HITL: '/hitl/reprompt',
  ACCEPT_PROPOSAL: '/hitl/proposal/accept',
  REJECT_PROPOSAL: '/hitl/proposal/reject',

  // Endpoints DDL Sandbox
  EXECUTE_SANDBOX: '/sandbox/execute',
  SIMULATE_TEST_DATA: '/sandbox/simulate-data',
} as const;
