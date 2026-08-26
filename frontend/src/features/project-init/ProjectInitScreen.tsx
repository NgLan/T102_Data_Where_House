"use client";

import { useCallback, useState } from "react";
import { ArrowRight, Save } from "lucide-react";
import { useTranslation } from "react-i18next";
import { MainLayout } from "@/common/components/layout/MainLayout";
import { Button } from "@/common/components/ui/button";
import { DataSourceSection } from "./project-init-screen/DataSourceSection";
import { useDataSources } from "./project-init-screen/data-sources/hooks/use-data-sources";
import { PiiGuardNotice } from "./project-init-screen/PiiGuardNotice";
import { ProjectInitSkeleton } from "./project-init-screen/ProjectInitSkeleton";
import { useProjectAnalysis } from "./project-init-screen/hooks/use-project-analysis";
import { useProjectInitWorkflow } from "./project-init-screen/hooks/use-project-init-workflow";
import { ProjectDetailsForm } from "./project-init-screen/ProjectDetailsForm";
import { useProjectDetails } from "./project-init-screen/project-details/hooks/use-project-details";
import { RequirementWorkspace } from "./project-init-screen/requirement-workspace/components/RequirementWorkspace";
import { useRequirementClarification } from "./project-init-screen/requirement-workspace/hooks/use-requirement-clarification";

/** Màn hình Project Init: lưu/phân tích tại chỗ và chỉ điều hướng bằng Continue. */
export function ProjectInitScreen({ projectId }: { projectId: string }) {
  const { t } = useTranslation("project-init");
  const [isChatOpen, setIsChatOpen] = useState(false);
  const project = useProjectDetails(projectId);
  const sources = useDataSources(projectId);
  const analysis = useProjectAnalysis(projectId);
  const clarification = useRequirementClarification(projectId);
  const handleOpenChat = useCallback(() => setIsChatOpen(true), []);
  const handleCloseChat = useCallback(() => setIsChatOpen(false), []);
  const workflow = useProjectInitWorkflow({
    projectId, project, clarification, analysis,
    onOpenChat: handleOpenChat,
    onCloseChat: handleCloseChat,
  });
  const isBusy = project.updateMutation.isPending ||
    project.rawRequirementMutation.isPending || sources.isMutating ||
    clarification.isProcessing || workflow.isRunning;
  const isAnalysisCurrent = Boolean(
    analysis.statusQuery.data &&
    !analysis.statusQuery.data.requirement_analysis_outdated &&
    !analysis.statusQuery.data.source_analysis_outdated,
  );
  const handleSaveDraft = async () => {
    try {
      await project.saveDraft();
    } catch {
      /* API layer owns toast. */
    }
  };
  const handleUploadSources = async (files: File[]) => {
    await sources.uploadCsvFiles(files);
  };
  const handleDeleteSource = async (sourceId: string) => {
    await sources.deleteSource(sourceId);
  };
  const isLoading =
    project.projectQuery.isLoading || sources.sourcesQuery.isLoading;
  return (
    <MainLayout selectedProjectId={projectId}>
      <section className="mx-auto w-full max-w-6xl space-y-5 pb-28">
        <header className="rounded-xl border bg-background p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold">{t("TXT_SCREEN_TITLE")}</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                {t("TXT_SCREEN_SUBTITLE")}
              </p>
            </div>
            {workflow.phase !== "IDLE" && (
              <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                {t(`TXT_WORKFLOW_${workflow.phase}`)}
              </span>
            )}
          </div>
        </header>
        {isLoading ? (
          <ProjectInitSkeleton />
        ) : project.projectQuery.isError ? (
          <LoadError onRetry={() => project.projectQuery.refetch()} />
        ) : (
          <>
            <ProjectDetailsForm
              form={project.form}
              disabled={!sources.canEdit || isBusy}
            />
            <div id="requirement-workspace">
              <RequirementWorkspace
                projectId={projectId}
                canEdit={sources.canEdit}
                form={project.form}
                isRawDirty={project.isRequirementDirty}
                isWorkflowRunning={workflow.isRunning}
                clarification={clarification}
                isChatOpen={isChatOpen}
                onChatOpenChange={setIsChatOpen}
                onSaveDraft={handleSaveDraft}
                onContinueAnalysis={workflow.continueAnalysis}
              />
            </div>
            <DataSourceSection
              projectId={projectId}
              sources={sources.sources}
              canEdit={sources.canEdit}
              disabled={isBusy}
              hasError={sources.sourcesQuery.isError}
              sourceCoverageBatch={workflow.sourceCoverageBatch}
              sourceRevision={workflow.sourceRevision}
              isSourceCoverageStale={workflow.isSourceCoverageStale}
              isRecheckingCoverage={workflow.phase === "RECHECKING_SOURCE"}
              pendingCoverageItemIds={analysis.pendingItemIds}
              coverageItemErrors={analysis.itemErrors}
              onResolveCoverage={(input) => void workflow.resolveCoverage(input)}
              onRecheckCoverage={(input) => void workflow.recheckCoverage(input)}
              onEditRequirement={() => document.getElementById("requirement-workspace")?.scrollIntoView({ behavior: "smooth" })}
              onDelete={(id) => void handleDeleteSource(id)}
              onReload={() => void sources.sourcesQuery.refetch()}
              onUpload={(files) => void handleUploadSources(files)}
            />
            <PiiGuardNotice />
            {!sources.canEdit && !isAnalysisCurrent && (
              <p className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">
                {t("TXT_MEMBER_ANALYSIS_OUTDATED")}
              </p>
            )}
            <div className="fixed inset-x-0 bottom-0 z-30 flex justify-end gap-3 border-t bg-background/95 px-6 py-4 shadow-[0_-8px_24px_-16px_rgba(0,0,0,0.45)] backdrop-blur">
              <Button type="button" size="lg" variant="outline"
                disabled={!sources.canEdit || isBusy || !project.form.formState.isDirty}
                onClick={() => void handleSaveDraft()}>
                <Save />{t("BTN_SAVE_DRAFT")}
              </Button>
              <Button
                type="button"
                size="lg"
                disabled={!sources.canEdit || isBusy}
                onClick={() => void workflow.run()}
              >
                {t(workflow.isRunning ? `TXT_WORKFLOW_${workflow.phase}` : "BTN_SAVE_AND_ANALYZE")}
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
