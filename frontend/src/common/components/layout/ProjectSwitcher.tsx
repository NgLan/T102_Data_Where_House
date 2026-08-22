"use client";

import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import { NativeSelect, NativeSelectOption } from "@/common/components/ui/native-select";
import { cn } from "@/common/lib/utils";
import { useAccessibleProjectsQuery } from "@/common/projects/project-queries";

interface ProjectSwitcherProps {
  selectedProjectId?: string;
}

/** Chuyển workspace bằng danh sách Project dùng chung trong query cache.
 * @param props Project hiện hành nếu đang ở workspace.
 * @returns Select điều hướng tới Project được chọn.
 */
export function ProjectSwitcher({ selectedProjectId }: ProjectSwitcherProps) {
  const router = useRouter();
  const { t } = useTranslation("common");
  const projectsQuery = useAccessibleProjectsQuery();
  const projects = projectsQuery.data ?? [];
  const placeholder = resolvePlaceholder(projectsQuery.status, projects.length, t);
  return (
    <NativeSelect className={cn("min-w-0 flex-1 sm:max-w-72",
      !selectedProjectId && "[&>select]:text-muted-foreground")}
      value={selectedProjectId ?? ""}
      disabled={projectsQuery.isPending || projectsQuery.isError || projects.length === 0}
      aria-label={t("PROJECT_SELECTOR_LABEL")}
      onChange={(event) => router.push(`/projects/${event.target.value}`)}>
      <NativeSelectOption value="" disabled>{placeholder}</NativeSelectOption>
      {projects.map((project) => (
        <NativeSelectOption key={project.id} value={project.id}>{project.name}</NativeSelectOption>
      ))}
    </NativeSelect>
  );
}

function resolvePlaceholder(
  status: "error" | "pending" | "success",
  projectCount: number,
  translate: (key: string) => string,
): string {
  if (status === "pending") return translate("TXT_PROJECT_SELECTOR_LOADING");
  if (status === "error") return translate("TXT_PROJECT_SELECTOR_ERROR");
  return projectCount > 0
    ? translate("PROJECT_SELECTOR_PLACEHOLDER")
    : translate("TXT_PROJECT_SELECTOR_EMPTY");
}
