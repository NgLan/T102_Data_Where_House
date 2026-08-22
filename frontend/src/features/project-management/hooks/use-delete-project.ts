"use client";

import { useMemo } from "react";
import { useMutation, useMutationState, useQueryClient } from "@tanstack/react-query";
import type { ProjectSummaryResponse } from "@/api";
import { useAppNotification } from "@/common/notifications";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { deleteProject } from "../services/project-mutations-api";

const DELETE_PROJECT_MUTATION_KEY = ["delete-project"] as const;

/** Xóa Project và đồng bộ shared project cache.
 * @returns Mutation function cùng tập ID đang được xóa đồng thời.
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();
  const { notifyError, notifySuccess } = useAppNotification();
  const mutation = useMutation({
    mutationKey: DELETE_PROJECT_MUTATION_KEY,
    mutationFn: deleteProject,
    onSuccess: (_, projectId) => {
      queryClient.setQueryData<ProjectSummaryResponse[]>(PROJECTS_QUERY_KEY, (projects = []) =>
        projects.filter((project) => project.id !== projectId));
      notifySuccess("MSG_PROJECT_DELETED");
    },
    onError: () => notifyError(),
  });
  const pendingIds = useMutationState<string>({
    filters: { mutationKey: DELETE_PROJECT_MUTATION_KEY, status: "pending" },
    select: (item) => item.state.variables as string,
  });
  return { deleteProject: mutation.mutateAsync, deletingProjectIds: useMemo(
    () => new Set(pendingIds), [pendingIds],
  ) };
}
