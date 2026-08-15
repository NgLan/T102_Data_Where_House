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
