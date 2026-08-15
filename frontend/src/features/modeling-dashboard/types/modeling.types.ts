/**
 * Types & Interfaces dành riêng cho Feature Modeling Dashboard
 */

import { ErdTableNodeDto, InsightItemDto } from '@/api/model/erd.dto';

export interface ModelingState {
  dbmlCode: string;
  tables: ErdTableNodeDto[];
  insights: InsightItemDto[];
  zoomLevel: number;
}

/** Payload backend trả về cho mô hình dữ liệu hiện hành của một dự án */
export interface DataModelResponseDto {
  id: string;
  project_id: string;
  dbml: string;
  revision: number;
  created_at: string;
  updated_at: string;
}
