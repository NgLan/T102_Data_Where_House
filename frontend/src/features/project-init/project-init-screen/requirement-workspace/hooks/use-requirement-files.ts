"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { projectInitQueryKeys } from "../../../constants/project-init-query-keys";
import { getProjectDetails } from "../../project-details/services/project-details-api";
import {
  requestRequirementFileDelete,
  requestRequirementFiles,
  requestRequirementFileUpload,
} from "../services/requirement-files-api";

/** Quản lý Requirement Documents và đồng bộ shared requirement revision. */
export function useRequirementFiles(projectId: string) {
  const queryClient = useQueryClient();
  const filesQuery = useQuery({
    queryKey: projectInitQueryKeys.requirementFiles(projectId),
    queryFn: () => requestRequirementFiles(projectId),
  });
  const refreshContext = async () => {
    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.project(projectId),
      }),
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.requirementFiles(projectId),
      }),
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.clarification(projectId),
      }),
    ]);
  };
  const uploadMutation = useMutation({
    mutationKey: ["upload-requirement-files", projectId],
    mutationFn: async (files: File[]) => {
      const project = await queryClient.fetchQuery({
        queryKey: projectInitQueryKeys.project(projectId),
        queryFn: () => getProjectDetails(projectId),
      });
      return requestRequirementFileUpload(
        projectId, files, project.requirement_revision,
      );
    },
    onSuccess: refreshContext,
  });
  const deleteMutation = useMutation({
    mutationKey: ["delete-requirement-file", projectId],
    mutationFn: async (fileId: string) => {
      const project = await queryClient.fetchQuery({
        queryKey: projectInitQueryKeys.project(projectId),
        queryFn: () => getProjectDetails(projectId),
      });
      return requestRequirementFileDelete(
        projectId, fileId, project.requirement_revision,
      );
    },
    onSuccess: refreshContext,
  });
  return {
    filesQuery,
    files: filesQuery.data?.items ?? [],
    canEdit: filesQuery.data?.can_edit ?? false,
    upload: uploadMutation.mutateAsync,
    deleteFile: deleteMutation.mutateAsync,
    isMutating: uploadMutation.isPending || deleteMutation.isPending,
  };
}
