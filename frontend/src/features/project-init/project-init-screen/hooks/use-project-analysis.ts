"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAppNotification } from "@/common/notifications";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { projectInitQueryKeys } from "../../constants/project-init-query-keys";
import { analyzeProject, getAnalysisStatus } from "../services/project-analysis-api";

/** Quản lý analysis status và mutation Analyze duy nhất của Project Init. */
export function useProjectAnalysis(projectId: string) {
  const queryClient = useQueryClient();
  const { notifySuccess } = useAppNotification();
  const statusQuery = useQuery({ queryKey: projectInitQueryKeys.status(projectId),
    queryFn: () => getAnalysisStatus(projectId) });
  const analysisMutation = useMutation({
    mutationKey: ["analyze-project", projectId], mutationFn: () => analyzeProject(projectId),
    onSuccess: async (action) => {
      await Promise.all([
        queryClient.refetchQueries({ queryKey: projectInitQueryKeys.project(projectId) }),
        queryClient.refetchQueries({ queryKey: projectInitQueryKeys.sources(projectId) }),
        queryClient.refetchQueries({ queryKey: projectInitQueryKeys.status(projectId) }),
        queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY }),
      ]);
      notifySuccess("MSG_PROJECT_ANALYSIS_COMPLETED");
      return action;
    },
  });
  return { analyze: analysisMutation.mutateAsync, analysisMutation, statusQuery };
}
