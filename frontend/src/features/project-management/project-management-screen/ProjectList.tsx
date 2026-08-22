import { FolderKanban, SearchX } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectSummaryResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { useAppNotification } from "@/common/notifications";
import { ProjectCard } from "./project-list/ProjectCard";
import { ProjectListFeedback } from "./project-list/ProjectListFeedback";
import { ProjectListSkeleton } from "./project-list/ProjectListSkeleton";

interface ProjectListProps {
  projects: ProjectSummaryResponse[];
  totalCount: number;
  errorCode: string;
  hasSearchQuery: boolean;
  isInitialError: boolean;
  isInitialLoading: boolean;
  deletingProjectIds: ReadonlySet<string>;
  onRetry: () => void;
  onClearSearch: () => void;
  onCreateProject: () => void;
  onDeleteProject: (projectId: string) => Promise<void>;
}

/** Chọn skeleton, feedback hoặc grid theo trạng thái project query.
 * @param props Query state, dữ liệu và callbacks của danh sách.
 * @returns Nội dung chính của danh sách Project.
 */
export function ProjectList(props: ProjectListProps) {
  const { t } = useTranslation("project-management");
  const { t: tCommon } = useTranslation("common");
  const { getErrorMessage } = useAppNotification();
  if (props.isInitialLoading) return <ProjectListSkeleton />;
  if (props.isInitialError)
    return (
      <ProjectListFeedback
        icon={<FolderKanban />}
        title={t("TXT_LOAD_ERROR_TITLE")}
        description={getErrorMessage(props.errorCode)}
        action={<Button onClick={props.onRetry}>{tCommon("BTN_RETRY")}</Button>}
      />
    );
  if (
    props.projects.length === 0 &&
    props.totalCount > 0 &&
    props.hasSearchQuery
  ) {
    return (
      <ProjectListFeedback
        icon={<SearchX />}
        title={t("TXT_NO_RESULTS_TITLE")}
        description={t("TXT_NO_RESULTS_DESCRIPTION")}
        action={
          <Button variant="outline" onClick={props.onClearSearch}>
            {t("BTN_CLEAR_SEARCH")}
          </Button>
        }
      />
    );
  }
  if (props.totalCount === 0)
    return (
      <ProjectListFeedback
        icon={<FolderKanban />}
        title={t("TXT_EMPTY_TITLE")}
        description={t("TXT_EMPTY_DESCRIPTION")}
        action={
          <Button onClick={props.onCreateProject}>
            {t("BTN_CREATE_PROJECT")}
          </Button>
        }
      />
    );
  return (
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      {props.projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          isDeleting={props.deletingProjectIds.has(project.id)}
          onDeleteProject={props.onDeleteProject}
        />
      ))}
    </div>
  );
}
