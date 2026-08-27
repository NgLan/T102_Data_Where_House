import Link from "next/link";
import { AlertTriangle, Calendar, Clock, FileSpreadsheet } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectSummaryResponse } from "@/api";
import { Badge } from "@/common/components/ui/badge";
import { PROJECT_DOMAIN_OPTIONS } from "@/common/projects/project-domain-options";
import {
  formatCalendarDate,
  formatFullDateTime,
  formatRelativeTime,
} from "@/common/utils/format-relative-time";
import { ProjectDeleteAction } from "./ProjectDeleteAction";

interface ProjectCardProps {
  project: ProjectSummaryResponse;
  isDeleting: boolean;
  onDeleteProject: (projectId: string) => Promise<void>;
}

/** Hiển thị thông tin tóm tắt và trạng thái Data Model của Project.
 * @param props Project, trạng thái xóa và callback action.
 * @returns Card có link mở workspace và action xóa riêng biệt.
 */
export function ProjectCard({
  project,
  isDeleting,
  onDeleteProject,
}: ProjectCardProps) {
  const { t, i18n } = useTranslation("project-management");
  const { t: tCommon } = useTranslation("common");
  const locale = i18n.resolvedLanguage;
  const relativeTime = formatRelativeTime(project.updated_at, tCommon, locale);
  const updatedLabel = tCommon("TXT_UPDATED_AT", { time: relativeTime });
  const createdDate = formatCalendarDate(project.created_at, locale);
  const createdLabel = tCommon("TXT_CREATED_AT", { date: createdDate });
  const domainOption = PROJECT_DOMAIN_OPTIONS.find(
    ({ value }) => value === project.domain,
  );
  const domainLabel = domainOption
    ? tCommon(domainOption.labelKey)
    : project.domain;
  return (
    <article className="flex min-h-52 flex-col rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-3 flex items-start justify-between gap-2 text-xs text-muted-foreground">
        <Badge variant="secondary">
          {domainLabel || t("TXT_CUSTOM_DOMAIN")}
        </Badge>
        <span
          className="flex shrink-0 items-center gap-1 cursor-default"
          title={formatFullDateTime(project.updated_at, locale)}
        >
          <Clock className="size-3" aria-hidden />
          <span>{updatedLabel}</span>
        </span>
      </div>
      <Link
        href={`/projects/${project.id}`}
        className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <h2 className="font-semibold text-foreground hover:text-primary">
          {project.name}
        </h2>
        {project.description && (
          <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
            {project.description}
          </p>
        )}
      </Link>
      {project.is_data_model_outdated && (
        <Badge variant="destructive" className="mt-3 w-fit">
          <AlertTriangle aria-hidden />
          {t("TXT_DBML_OUTDATED")}
        </Badge>
      )}
      <div className="mt-auto flex items-center justify-between border-t pt-3 text-xs text-muted-foreground">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="flex items-center gap-1">
            <FileSpreadsheet className="size-3.5" />
            {t("TXT_SOURCE_COUNT", { count: project.data_source_count })}
          </span>
          <span
            className="flex items-center gap-1 cursor-default"
            title={formatFullDateTime(project.created_at, locale)}
          >
            <Calendar className="size-3.5" />
            {createdLabel}
          </span>
        </div>
        <ProjectDeleteAction
          projectId={project.id}
          projectName={project.name}
          isDeleting={isDeleting}
          onDeleteProject={onDeleteProject}
        />
      </div>
    </article>
  );
}
