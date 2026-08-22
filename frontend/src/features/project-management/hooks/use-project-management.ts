"use client";

import { useState } from "react";
import { isApiError } from "@/api";
import { useAccessibleProjectsQuery } from "@/common/projects/project-queries";
import { useCreateProject } from "./use-create-project";
import { useDeleteProject } from "./use-delete-project";
import { useProjectSearch } from "./use-project-search";

/** Ghép state giao diện với project query và mutations.
 * @returns View model duy nhất cho ProjectManagementScreen.
 */
export function useProjectManagement() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const projectsQuery = useAccessibleProjectsQuery();
  const projects = projectsQuery.data ?? [];
  const search = useProjectSearch(projects);
  const createMutation = useCreateProject({ onCreated: () => setIsCreateDialogOpen(false) });
  const deletion = useDeleteProject();
  return {
    ...search,
    ...deletion,
    createProject: createMutation.mutateAsync,
    errorCode: isApiError(projectsQuery.error) ? projectsQuery.error.errorCode : "UNKNOWN_ERROR",
    isCreateDialogOpen,
    isInitialError: projectsQuery.isError && projects.length === 0,
    isInitialLoading: projectsQuery.isPending,
    isRefreshing: projectsQuery.isFetching && !projectsQuery.isPending,
    projects,
    refreshProjects: () => { void projectsQuery.refetch(); },
    setIsCreateDialogOpen,
  };
}
