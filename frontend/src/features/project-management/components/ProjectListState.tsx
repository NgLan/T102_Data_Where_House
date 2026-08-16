import { FolderKanban, SearchX } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectSummaryResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import type { ProjectListStatus } from "../hooks/use-project-management";
import { ProjectCard } from "./ProjectCard";
import { ProjectListSkeleton } from "./ProjectListSkeleton";

interface ProjectListStateProps {
  projects: ProjectSummaryResponse[];
  totalCount: number;
  status: ProjectListStatus;
  errorCode: string;
  hasSearch: boolean;
  deletingIds: ReadonlySet<string>;
  onRetry: () => void;
  onClearSearch: () => void;
  onCreate: () => void;
  onDelete: (projectId: string) => Promise<void>;
}

/** Chọn đúng initial/error/empty/no-results/content state. */
export function ProjectListState(props: ProjectListStateProps) {
  const { t } = useTranslation("project-management");
  const { getErrorMessage } = useAppNotification();
  if (props.status === "initial-loading") return <ProjectListSkeleton />;
  if (props.status === "error")
    return (
      <State
        icon={<FolderKanban />}
        title={t("LOAD_ERROR_TITLE")}
        description={getErrorMessage(props.errorCode)}
        action={<Button onClick={props.onRetry}>{t("RETRY")}</Button>}
      />
    );
  if (props.projects.length === 0 && props.totalCount > 0 && props.hasSearch)
    return (
      <State
        icon={<SearchX />}
        title={t("NO_RESULTS_TITLE")}
        description={t("NO_RESULTS_DESCRIPTION")}
        action={
          <Button variant="outline" onClick={props.onClearSearch}>
            {t("CLEAR_SEARCH")}
          </Button>
        }
      />
    );
  if (props.totalCount === 0)
    return (
      <State
        icon={<FolderKanban />}
        title={t("EMPTY_TITLE")}
        description={t("EMPTY_DESCRIPTION")}
        action={<Button onClick={props.onCreate}>{t("CREATE_PROJECT")}</Button>}
      />
    );
  return (
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      {props.projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          isDeleting={props.deletingIds.has(project.id)}
          onDelete={props.onDelete}
        />
      ))}
    </div>
  );
}

function State({
  icon,
  title,
  description,
  action,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  action: React.ReactNode;
}) {
  return (
    <section className="flex flex-col items-center gap-3 rounded-xl border border-dashed p-12 text-center">
      <span className="text-primary">{icon}</span>
      <h2 className="font-semibold">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      {action}
    </section>
  );
}
