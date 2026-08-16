"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, Save } from "lucide-react";
import { useTranslation } from "react-i18next";
import { MainLayout } from "@/common/components/layout/MainLayout";
import { Button } from "@/common/components/ui/button";
import { createWorkflowHref } from "@/common/routing/workflow-routing";
import { ProjectInitSkeleton } from "./components/ProjectInitSkeleton";
import { DataSourceSection } from "./data-sources/components/DataSourceSection";
import { useDataSources } from "./data-sources/hooks/use-data-sources";
import { PiiGuardNotice } from "./pii-guard/components/PiiGuardNotice";
import { ProjectDetailsForm } from "./project-details/components/ProjectDetailsForm";
import { useProjectDetails } from "./project-details/hooks/use-project-details";

interface ProjectInitScreenProps {
  projectId: string;
}

/** Màn hình Step 1 cho một project hiện hữu.
 * @param props ID Project lấy trực tiếp từ route workspace.
 * @returns Màn hình chỉnh thông tin Project và quản lý Data Source.
 */
export function ProjectInitScreen({ projectId }: ProjectInitScreenProps) {
  const { t } = useTranslation("project-init");
  const router = useRouter();
  const project = useProjectDetails(projectId);
  const sources = useDataSources(projectId, project.appendRequirement);
  const isBusy = project.isSaving || sources.isMutating;
  const continueToModeling = async () => {
    const saved = sources.canEdit ? await project.save() : true;
    if (saved) router.push(createWorkflowHref("modeling", projectId));
  };
  return (
    <MainLayout>
      <main className="mx-auto w-full max-w-6xl space-y-5 pb-10">
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
        {project.isLoading || sources.isLoading ? (
          <ProjectInitSkeleton />
        ) : project.loadError ? (
          <LoadError onRetry={project.reload} />
        ) : (
          <>
            <ProjectDetailsForm
              form={project.form}
              errors={project.errors}
              disabled={!sources.canEdit || isBusy}
              onChange={project.updateField}
            />
            <DataSourceSection
              projectId={projectId}
              sources={sources.sources}
              canEdit={sources.canEdit}
              disabled={isBusy}
              loadError={sources.loadError}
              onDelete={sources.deleteSource}
              onReload={sources.reload}
              onUpdate={sources.updateColumn}
              onUpload={sources.uploadFiles}
            />
            <PiiGuardNotice />
            <div className="flex justify-end">
              <Button
                type="button"
                size="lg"
                disabled={isBusy}
                onClick={() => void continueToModeling()}
              >
                {sources.canEdit ? <Save /> : <ArrowRight />}
                {project.isSaving
                  ? t("MSG_SAVING")
                  : sources.canEdit
                    ? t("BTN_SAVE_CONTINUE")
                    : t("BTN_CONTINUE")}
              </Button>
            </div>
          </>
        )}
      </main>
    </MainLayout>
  );
}

function LoadError({ onRetry }: { onRetry: () => void }) {
  const { t } = useTranslation("project-init");
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
        {t("BTN_RETRY")}
      </Button>
    </section>
  );
}
