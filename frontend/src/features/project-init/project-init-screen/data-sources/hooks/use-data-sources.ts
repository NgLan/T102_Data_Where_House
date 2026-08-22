"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAppNotification } from "@/common/notifications";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { projectInitQueryKeys } from "../../../constants/project-init-query-keys";
import {
  deleteDataSource,
  listDataSources,
  uploadDataSources,
} from "../services/data-sources-api";
import { validateCsvFiles } from "../utils/data-source-upload-validation";

/** Quản lý server state Data Source bằng TanStack Query. */
export function useDataSources(projectId: string) {
  const queryClient = useQueryClient();
  const { notifyError, notifySuccess } = useAppNotification();
  const sourcesQuery = useQuery({
    queryKey: projectInitQueryKeys.sources(projectId),
    queryFn: () => listDataSources(projectId),
  });
  const refreshSources = async () => {
    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.sources(projectId),
      }),
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.status(projectId),
      }),
      queryClient.invalidateQueries({
        queryKey: projectInitQueryKeys.project(projectId),
      }),
      queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY }),
    ]);
  };
  const uploadMutation = useMutation({
    mutationKey: ["upload-project-sources", projectId],
    mutationFn: (files: File[]) => uploadDataSources(projectId, files),
    onSuccess: async (result) => {
      await refreshSources();
      notifySuccess("MSG_DATA_SOURCES_UPLOADED", {
        params: { count: result.total_files_uploaded },
      });
    },
  });
  const deleteMutation = useMutation({
    mutationKey: ["delete-project-source", projectId],
    mutationFn: (sourceId: string) => deleteDataSource(projectId, sourceId),
    onSuccess: async () => {
      await refreshSources();
      notifySuccess("MSG_DATA_SOURCE_DELETED");
    },
  });
  const uploadCsvFiles = async (files: File[]) => {
    const errorCode = validateCsvFiles(files, sourcesQuery.data?.items ?? []);
    if (errorCode) return notifyError(errorCode);
    await uploadMutation.mutateAsync(files);
  };
  return {
    canEdit: sourcesQuery.data?.can_edit ?? false,
    deleteSource: deleteMutation.mutateAsync,
    isMutating: uploadMutation.isPending || deleteMutation.isPending,
    sources: sourcesQuery.data?.items ?? [],
    sourcesQuery,
    uploadCsvFiles,
  };
}
