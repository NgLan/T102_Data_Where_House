/**
 * Types & Interfaces cho Feature Sandbox Deployment & DDL Editor
 */

import { TerminalLogEntryDto } from '@/api/model/sandbox.dto';

export interface SandboxConfigState {
  hostConnection: string;
  targetDatabase: string;
}

export interface SandboxDeploymentState {
  ddlScript: string;
  logs: TerminalLogEntryDto[];
  isDeploying: boolean;
}

/** Hệ quản trị CSDL đích khi sinh mã DDL (khớp enum SqlDialect của Backend) */
export type SqlDialect = 'postgresql' | 'snowflake' | 'bigquery';

/** Danh sách dialect hiển thị trên dropdown chọn Hệ quản trị CSDL (UC5.5) */
export const SQL_DIALECT_OPTIONS: readonly SqlDialect[] = [
  'postgresql',
  'snowflake',
  'bigquery',
] as const;

/** Payload backend trả về khi sinh mã DDL từ mô hình dữ liệu */
export interface DdlGenerationResponseDto {
  data_model_id: string;
  revision: number;
  dialect: SqlDialect;
  schema_name: string;
  ddl: string;
  table_count: number;
  warnings: string[];
}
