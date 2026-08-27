"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import { NativeSelect, NativeSelectOption } from "@/common/components/ui/native-select";
import { cn } from "@/common/lib/utils";
import { useAccessibleProjectsQuery } from "@/common/projects/project-queries";
import { CreateProjectDialog } from "@/features/project-management/project-management-screen/project-creation/components/CreateProjectDialog";
import { useCreateProject } from "@/features/project-management/hooks/use-create-project";

interface ProjectSwitcherProps {
  selectedProjectId?: string;
}

const CREATE_PROJECT_VALUE = "__create_new__";

/** Chuyển workspace bằng danh sách Project dùng chung trong query cache hoặc tạo mới.
 * @param props Project hiện hành nếu đang ở workspace.
 * @returns Select điều hướng tới Project được chọn kèm action tạo dự án.
 */
export function ProjectSwitcher({ selectedProjectId }: ProjectSwitcherProps) {
  const router = useRouter();
  const { t } = useTranslation("common");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const projectsQuery = useAccessibleProjectsQuery();
  const createMutation = useCreateProject({ onCreated: () => setIsCreateOpen(false) });
  const projects = projectsQuery.data ?? [];
  const placeholder = resolvePlaceholder(projectsQuery.status, projects.length, t);

  const handleChange = (value: string) => {
    if (value === CREATE_PROJECT_VALUE) {
      setIsCreateOpen(true);
      return;
    }
    if (value) router.push(`/projects/${value}`);
  };

  return (
    <>
      <NativeSelect
        className={cn("min-w-0 flex-1 sm:max-w-72", !selectedProjectId && "[&>select]:text-muted-foreground")}
        value={selectedProjectId ?? ""}
        disabled={projectsQuery.isPending || projectsQuery.isError}
        aria-label={t("PROJECT_SELECTOR_LABEL")}
        onChange={(event) => handleChange(event.target.value)}
      >
        <NativeSelectOption value="" disabled>{placeholder}</NativeSelectOption>
        <NativeSelectOption
          value={CREATE_PROJECT_VALUE}
          className="font-semibold text-primary"
          style={{ color: "hsl(var(--primary))", fontWeight: "bold" }}
        >
          {t("TXT_PROJECT_SELECTOR_CREATE")}
        </NativeSelectOption>
        {projects.map((project) => (
          <NativeSelectOption key={project.id} value={project.id}>
            {project.name}
          </NativeSelectOption>
        ))}
      </NativeSelect>
      <CreateProjectDialog
        isOpen={isCreateOpen}
        onOpenChange={setIsCreateOpen}
        onSubmit={async (body) => createMutation.mutateAsync(body)}
      />
    </>
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
