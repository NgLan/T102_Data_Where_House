/**
 * Định nghĩa DTO cho Xuất DDL và Thử nghiệm Sandbox
 */

/** Engine đã có driver thực trong backend. */
export type SandboxDbType = 'POSTGRESQL';

/**
 * Payload cấu hình kết nối Sandbox DB
 */
export interface SandboxConfigRequestDto {
  db_type: SandboxDbType;
  host: string;
  port: number;
  database_name: string;
  username?: string;
  password?: string;
  schema_name?: string;
}

/**
 * Phản hồi thông tin cấu hình Sandbox DB từ Backend
 */
export interface SandboxConfigResponseDto {
  id: string;
  project_id: string;
  db_type: SandboxDbType;
  host: string;
  port: number;
  database_name: string;
  username?: string;
  schema_name?: string;
  status: string;
}

/**
 * Yêu cầu kiểm tra thử kết nối DB
 */
export interface TestConnectionRequestDto {
  db_type: SandboxDbType;
  host: string;
  port: number;
  database_name: string;
  username?: string;
  password?: string;
  schema_name?: string;
}

/**
 * Kết quả kiểm tra kết nối DB
 */
export interface TestConnectionResponseDto {
  success: boolean;
  message: string;
  latency_ms?: number;
}

/**
 * Log dòng thực thi câu lệnh SQL
 */
export interface StatementLogDto {
  statement: string;
  is_success: boolean;
  execution_time_ms: number;
  timestamp: string;
  error_detail?: string;
}

/**
 * Log dòng terminal thực thi trên UI
 */
export interface TerminalLogEntryDto {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error';
}

/**
 * Payload gửi thực thi DDL script
 */
export interface ExecuteDdlRequestDto {
  ddl_script: string;
}

/**
 * Kết quả thực thi DDL trên Sandbox DB
 */
export interface SandboxExecutionResponseDto {
  success: boolean;
  executed_statements: number;
  succeeded_statements: number;
  failed_statements: number;
  total_duration_ms: number;
  logs: StatementLogDto[];
}

/** DDL sinh từ Data Model hiện tại. */
export interface DataModelDdlResponseDto {
  ddl: string;
  dialect: 'postgresql';
  revision: number;
}
