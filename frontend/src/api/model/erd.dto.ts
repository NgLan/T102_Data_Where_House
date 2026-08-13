/**
 * Định nghĩa DTO cho Mô hình ERD, DBML DSL và AI Insights
 */

/**
 * Kiểu cảnh báo từ AI Insights
 */
export type InsightSeverity = 'info' | 'error' | 'warn';

/**
 * Chi tiết từng mục cảnh báo AI Insights
 */
export interface InsightItemDto {
  id: string;
  table_name: string;
  severity: InsightSeverity;
  title: string;
  description: string;
}

/**
 * Định nghĩa thuộc tính trường (column) trong bảng ERD
 */
export interface ErdFieldDto {
  name: string;
  type: string;
  is_pk?: boolean;
  is_fk?: boolean;
  ref_table?: string;
  is_nullable?: boolean;
}

/**
 * Thẻ node bảng trong sơ đồ ERD
 */
export interface ErdTableNodeDto {
  table_name: string;
  table_type: 'fact' | 'dimension';
  fields: ErdFieldDto[];
  position?: { top: number; left: number };
}

/**
 * Phản hồi sinh mã DBML và ERD từ AI Agent
 */
export interface ErdGenerationResponseDto {
  dbml_script: string;
  tables: ErdTableNodeDto[];
  insights: InsightItemDto[];
}
