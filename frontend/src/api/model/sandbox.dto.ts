/**
 * Định nghĩa DTO cho Xuất DDL và Thử nghiệm Sandbox
 */

/**
 * Payload cấu hình kết nối Sandbox DB
 */
export interface SandboxConfigRequestDto {
  host: string;
  database: string;
  schema: string;
}

/**
 * Log dòng terminal thực thi
 */
export interface TerminalLogEntryDto {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error';
}

/**
 * Kết quả thực thi DDL trên Sandbox DB
 */
export interface SandboxExecutionResponseDto {
  success: boolean;
  executed_statements: number;
  logs: TerminalLogEntryDto[];
}
