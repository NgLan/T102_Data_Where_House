"use client";

import { MainLayout } from "@/common/components/layout/MainLayout";
import { AIInsightsPanel } from "./ai-insights/components/AIInsightsPanel";
import { useAiInsights } from "./ai-insights/hooks/use-ai-insights";
import { ModelingWorkspace } from "./modeling-workspace/components/ModelingWorkspace";

interface ModelingDashboardScreenProps {
  projectId: string;
}

/** Điều phối màn hình Modeling và điều hướng hai bước liền kề.
 * @param props ID Project lấy trực tiếp từ route workspace.
 * @returns Feature screen toàn chiều rộng cho DBML, ERD và AI insights.
 */
export function ModelingDashboardScreen({ projectId }: ModelingDashboardScreenProps) {
  const insights = useAiInsights();
  return (
    <MainLayout isFullWidth isFlush>
      <div className="flex h-full min-h-0 w-full flex-1 flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-300">
        <ModelingWorkspace projectId={projectId} />
        <AIInsightsPanel
          isOpen={insights.isWidgetOpen}
          onToggle={insights.toggleWidget}
          selectedFilter={insights.selectedTableFilter}
          onFilterChange={insights.setSelectedTableFilter}
          insights={insights.insights}
          tableNames={insights.tableNames}
          totalCount={insights.totalCount}
        />
      </div>
    </MainLayout>
  );
}
