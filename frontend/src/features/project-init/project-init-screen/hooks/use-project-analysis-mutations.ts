"use client";

import { useMutation, type QueryClient, type QueryKey } from "@tanstack/react-query";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { projectInitQueryKeys } from "../../constants/project-init-query-keys";
import {
  analyzeProject,
  initializeProject,
  recheckSourceCoverage,
  resolveSourceCoverage,
} from "../services/project-analysis-api";

export interface CoverageResolutionInput {
  assessmentId: string;
  batchId: string;
  expectedSourceRevision: number;
  expectedResolutionRevision: number;
  action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES";
  candidateId?: string;
}

export function useAnalysisMutation(
  projectId: string,
  queryClient: QueryClient,
) {
  return useMutation({
    mutationKey: ["analyze-project", projectId],
    mutationFn: () => analyzeProject(projectId),
    onSuccess: async () => {
      await refreshProjectState(queryClient, projectId);
    },
  });
}

export function useInitializationMutation(
  projectId: string,
  queryClient: QueryClient,
) {
  return useMutation({
    mutationKey: ["initialize-project", projectId],
    mutationFn: () => initializeProject(projectId),
    onSuccess: () => refreshProjectState(queryClient, projectId, true),
  });
}

export function useResolutionMutation(
  projectId: string,
  queryClient: QueryClient,
  notifySuccess: (key: "MSG_SOURCE_CONFIRMATION_SAVED") => void,
) {
  return useMutation({
    mutationKey: ["resolve-source-coverage", projectId],
    mutationFn: (input: CoverageResolutionInput) => resolveSourceCoverage(
      projectId, input.assessmentId, input.batchId,
      input.expectedSourceRevision, input.expectedResolutionRevision,
      input.action, input.candidateId,
    ),
    onSuccess: (status) => {
      queryClient.setQueryData(projectInitQueryKeys.status(projectId), status);
      notifySuccess("MSG_SOURCE_CONFIRMATION_SAVED");
    },
  });
}

export function useRecheckMutation(
  projectId: string,
  queryClient: QueryClient,
  notifySuccess: (key: "MSG_SOURCE_COVERAGE_RECHECKED") => void,
) {
  return useMutation({
    mutationKey: ["recheck-source-coverage", projectId],
    mutationFn: (input: { batchId: string; expectedSourceRevision: number }) =>
      recheckSourceCoverage(projectId, input.batchId, input.expectedSourceRevision),
    onSuccess: async (status) => {
      queryClient.setQueryData(projectInitQueryKeys.status(projectId), status);
      await refreshProjectState(queryClient, projectId);
      notifySuccess("MSG_SOURCE_COVERAGE_RECHECKED");
    },
    onError: () => refreshProjectState(queryClient, projectId),
  });
}

async function refreshProjectState(
  queryClient: QueryClient,
  projectId: string,
  includeClarification = false,
): Promise<void> {
  const queries: QueryKey[] = [
    projectInitQueryKeys.project(projectId),
    projectInitQueryKeys.sources(projectId),
    projectInitQueryKeys.status(projectId),
  ];
  if (includeClarification) queries.push(projectInitQueryKeys.clarification(projectId));
  await Promise.all([
    ...queries.map((queryKey) => queryClient.refetchQueries({ queryKey })),
    queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY }),
  ]);
}
