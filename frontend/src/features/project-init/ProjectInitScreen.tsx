"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, Save } from "lucide-react";
import { useTranslation } from "react-i18next";
import { MainLayout } from "@/common/components/layout/MainLayout";
import { Button } from "@/common/components/ui/button";
import { createWorkflowHref } from "@/common/routing/workflow-routing";
import { DataSourceSection } from "./project-init-screen/DataSourceSection";
import { useDataSources } from "./project-init-screen/data-sources/hooks/use-data-sources";
import { PiiGuardNotice } from "./project-init-screen/PiiGuardNotice";
import { ProjectInitSkeleton } from "./project-init-screen/ProjectInitSkeleton";
import { useProjectAnalysis } from "./project-init-screen/hooks/use-project-analysis";
import { ProjectDetailsForm } from "./project-init-screen/ProjectDetailsForm";
import { useProjectDetails } from "./project-init-screen/project-details/hooks/use-project-details";

/** Màn hình Project Init: lưu/phân tích tại chỗ và chỉ điều hướng bằng Continue. */
export function ProjectInitScreen({ projectId }: { projectId: string }) {
  const { t } = useTranslation("project-init");
  const router = useRouter();
  const project = useProjectDetails(projectId);
  const sources = useDataSources(projectId);
  const analysis = useProjectAnalysis(projectId);
  const isBusy =
    project.updateMutation.isPending ||
    sources.isMutating ||
    analysis.analysisMutation.isPending;
  const isAnalysisCurrent = Boolean(
    analysis.statusQuery.data &&
    !analysis.statusQuery.data.requirement_analysis_outdated &&
    !analysis.statusQuery.data.source_analysis_outdated,
  );
  const canContinue =
    !project.form.formState.isDirty && !isBusy && isAnalysisCurrent;
  const handleSaveAndAnalyze = async () => {
    try {
      if (!(await project.save())) return;
      const action = await analysis.analyze();
      if (action === "generated") {
        router.push(createWorkflowHref("modeling", projectId));
      }
    } catch {
      /* API layer owns toast. */
    }
  };
  const handleContinue = () =>
    router.push(createWorkflowHref("modeling", projectId));
  const isLoading =
    project.projectQuery.isLoading || sources.sourcesQuery.isLoading;
  return (
    <MainLayout selectedProjectId={projectId}>
      <section className="mx-auto w-full max-w-6xl space-y-5 pb-10">
        <header className="flex items-start justify-between gap-4 rounded-xl border bg-background p-5">
          <div>
            <h1 className="text-xl font-bold">{t("TXT_SCREEN_TITLE")}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("TXT_SCREEN_SUBTITLE")}
            </p>
          </div>
          <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            {t("TXT_STEP_PROGRESS")}
          </span>
        </header>
        {isLoading ? (
          <ProjectInitSkeleton />
        ) : project.projectQuery.isError ? (
          <LoadError onRetry={() => project.projectQuery.refetch()} />
        ) : (
          <>
            <ProjectDetailsForm
              form={project.form}
              requirements={project.projectQuery.data?.requirements ?? []}
              disabled={!sources.canEdit || isBusy}
            />
            <DataSourceSection
              projectId={projectId}
              sources={sources.sources}
              canEdit={sources.canEdit}
              disabled={isBusy}
              hasError={sources.sourcesQuery.isError}
              onDelete={(id) => void sources.deleteSource(id)}
              onReload={() => void sources.sourcesQuery.refetch()}
              onUpload={(files) => void sources.uploadCsvFiles(files)}
            />
            <PiiGuardNotice />
            {!sources.canEdit && !isAnalysisCurrent && (
              <p className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">
                {t("TXT_MEMBER_ANALYSIS_OUTDATED")}
              </p>
            )}
            <div className="flex flex-wrap justify-end gap-3">
              {sources.canEdit && (
                <Button
                  type="button"
                  size="lg"
                  disabled={isBusy}
                  onClick={() => void handleSaveAndAnalyze()}
                >
                  <Save />
                  {isBusy
                    ? t(
                        analysis.analysisMutation.isPending
                          ? "MSG_ANALYZING"
                          : "MSG_SAVING",
                      )
                    : t("BTN_SAVE_ANALYZE")}
                </Button>
              )}
              <Button
                type="button"
                size="lg"
                variant="outline"
                disabled={!canContinue}
                onClick={handleContinue}
              >
                {t("BTN_CONTINUE")}
                <ArrowRight />
              </Button>
            </div>
          </>
        )}
      </section>
    </MainLayout>
  );
}

function LoadError({ onRetry }: { onRetry: () => void }) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  return (
    <section className="rounded-xl border border-destructive/30 bg-background p-8 text-center">
      <h2 className="font-semibold">{t("TXT_PROJECT_LOAD_ERROR_TITLE")}</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        {t("TXT_PROJECT_LOAD_ERROR_DESCRIPTION")}
      </p>
      <Button
        className="mt-4"
        type="button"
        variant="outline"
        onClick={onRetry}
      >
        {tCommon("BTN_RETRY")}
      </Button>
    </section>
  );
}
