"use client";

import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { createDemoAIInsights } from "../utils/create-demo-ai-insights";

/** Quản lý trạng thái mở và bộ lọc của AI insights.
 * @returns Widget state, danh sách đã lọc và các callback cập nhật.
 */
export function useAiInsights() {
  const { t } = useTranslation("modeling-dashboard");
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [selectedTableFilter, setSelectedTableFilter] = useState("ALL");
  const insights = useMemo(() => createDemoAIInsights(t), [t]);
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
  };
}
