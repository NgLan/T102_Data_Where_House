"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiClient, getProjectAnalysisStatus, requireApiData } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/common/components/ui/empty";
import { Skeleton } from "@/common/components/ui/skeleton";
import { createWorkflowHref, type WorkflowStep } from "@/common/routing/workflow-routing";

interface DataModelStepGateProps {
  projectId: string;
  currentStep: Exclude<WorkflowStep, "project-init">;
  children: React.ReactNode;
}

/** Chặn bước 2/3 trước khi mount feature hooks nếu Project chưa có Data Model.
 * @param props ID project, bước hiện tại và nội dung children.
 * @returns Children khi có data model hoặc màn hình Empty điều hướng về bước 1.
 */
export function DataModelStepGate(props: DataModelStepGateProps) {
  const { t } = useTranslation("common");
  const query = useQuery({
    queryKey: ["project-init", "status", props.projectId],
    queryFn: async () => requireApiData((await getProjectAnalysisStatus({
      client: apiClient, path: { project_id: props.projectId },
      responseStyle: "fields", throwOnError: true,
    })).data),
  });

  if (query.isLoading) {
    return <div className="flex flex-1 min-h-72 p-4"><Skeleton className="size-full flex-1" /></div>;
  }

  if (!query.data?.data_model_exists) {
    return (
      <div className="flex min-h-0 flex-1 flex-col gap-3 p-4">
        <Empty className="min-h-72 flex-1 border">
          <EmptyHeader>
            <EmptyTitle>{t("TXT_DATA_MODEL_UNAVAILABLE_TITLE")}</EmptyTitle>
            <EmptyDescription>{t("TXT_DATA_MODEL_UNAVAILABLE_DESCRIPTION")}</EmptyDescription>
            <Button asChild>
              <Link href={createWorkflowHref("project-init", props.projectId)}>
                {t("BTN_BACK_TO_PROJECT_INIT")}
              </Link>
            </Button>
          </EmptyHeader>
        </Empty>
      </div>
    );
  }

  return <>{props.children}</>;
}
