/** API đọc insight được phân tích từ Data Model hiện tại. */

import { apiClient } from '@/api/http/client';
import type { ApiResponse } from '@/api/model/common-response.dto';
import type { AIInsight, AIInsightSeverity } from '../types/ai-insight-types';

interface DataModelInsightDto {
  id: string;
  table_name: string;
  severity: AIInsightSeverity;
  title: string;
  description: string;
}

export async function getDataModelInsightsApi(projectId: string): Promise<AIInsight[]> {
  const response: ApiResponse<DataModelInsightDto[]> = await apiClient.get(
    `/projects/${projectId}/data-model/insights`
  );
  return response.data.map((item) => ({
    id: item.id,
    tableName: item.table_name,
    severity: item.severity,
    title: item.title,
    description: item.description,
  }));
}
