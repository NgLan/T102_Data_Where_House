"use client";

import { MainLayout } from "@/common/components/layout/MainLayout";
import { ModelingWorkspace } from "./modeling-workspace/ModelingWorkspace";

interface ModelingDashboardScreenProps {
  projectId: string;
}

/** Điều phối màn hình Modeling và điều hướng hai bước liền kề.
 * @param props ID Project lấy trực tiếp từ route workspace.
 * @returns Feature screen toàn chiều rộng cho DBML, ERD và AI insights.
 */
export function ModelingDashboardScreen({
  projectId,
}: ModelingDashboardScreenProps) {
  return (
    <MainLayout isFullWidth isFlush selectedProjectId={projectId}>
      <div className="flex h-full min-h-0 w-full flex-1 flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-300">
        <ModelingWorkspace projectId={projectId} />
      </div>
    </MainLayout>
  );
}
