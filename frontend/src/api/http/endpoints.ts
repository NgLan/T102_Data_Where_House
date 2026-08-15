/**
 * Danh sách hằng số API Endpoints cho hệ thống Backend
 */

export const API_ENDPOINTS = {
  // Endpoints khởi tạo & dữ liệu nguồn
  PROJECT_INIT: '/projects/init',
  UPLOAD_DATA_SOURCE: '/projects/upload-datasource',
  
  // Endpoints mô hình hóa & AI Agent ERD
  GENERATE_ERD: '/modeling/generate-erd',
  UPDATE_DBML: '/modeling/update-dbml',
  GET_INSIGHTS: '/modeling/insights',

  // Data Model hiện tại và chỉnh sửa trực quan UC5.1.3
  DATA_MODEL: (projectId: string) => `/projects/${projectId}/data-model`,
  
  // Endpoints HITL Editor & Proposal Review
  REPROMPT_HITL: '/hitl/reprompt',
  ACCEPT_PROPOSAL: '/hitl/proposal/accept',
  REJECT_PROPOSAL: '/hitl/proposal/reject',
  
  // Endpoints DDL Sandbox
  GENERATE_DDL: '/sandbox/generate-ddl',
  EXECUTE_SANDBOX: '/sandbox/execute',
  SIMULATE_TEST_DATA: '/sandbox/simulate-data',
} as const;
