"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { AIInsight } from "../types/ai-insight-types";
import { getDataModelInsightsApi } from "../services/ai-insights-api";

/** Quản lý trạng thái mở và bộ lọc của AI insights.
 * @returns Widget state, danh sách đã lọc và các callback cập nhật.
 */
export function useAiInsights(projectId: string | null) {
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [selectedTableFilter, setSelectedTableFilter] = useState("ALL");
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const reload = useCallback(async () => {
    if (!projectId) {
      setInsights([]);
      setErrorMessage("Chưa có project để tải nội dung phân tích.");
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setInsights(await getDataModelInsightsApi(projectId));
    } catch (error) {
      setInsights([]);
      setErrorMessage(error instanceof Error ? error.message : "Không thể tải nội dung phân tích.");
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);
  useEffect(() => {
    const timeoutId = window.setTimeout(() => void reload(), 0);
    return () => window.clearTimeout(timeoutId);
  }, [reload]);
  const filteredInsights = useMemo(
    () =>
      selectedTableFilter === "ALL"
        ? insights
        : insights.filter((item) => item.tableName === selectedTableFilter),
    [insights, selectedTableFilter],
  );
  return {
    isWidgetOpen,
    toggleWidget: () => setIsWidgetOpen((current) => !current),
    selectedTableFilter,
    setSelectedTableFilter,
    insights: filteredInsights,
    tableNames: [...new Set(insights.map((item) => item.tableName))],
    totalCount: insights.length,
    isLoading,
    errorMessage,
    reload,
  };
}
