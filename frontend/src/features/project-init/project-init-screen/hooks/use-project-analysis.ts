"use client";

import { useCallback, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAppNotification } from "@/common/notifications";
import { projectInitQueryKeys } from "../../constants/project-init-query-keys";
import { getSourceCoverage } from "../services/project-analysis-api";
import {
  useAnalysisMutation,
  useInitializationMutation,
  useRecheckMutation,
  useResolutionMutation,
  type CoverageResolutionInput,
} from "./use-project-analysis-mutations";

/** Server state and focused mutations used by Project Init analysis workflow. */
export function useProjectAnalysis(projectId: string) {
  const queryClient = useQueryClient();
  const { notifySuccess } = useAppNotification();
  const statusQuery = useQuery({
    queryKey: projectInitQueryKeys.status(projectId),
    queryFn: () => getSourceCoverage(projectId),
  });
  const analysisMutation = useAnalysisMutation(projectId, queryClient);
  const initializationMutation = useInitializationMutation(projectId, queryClient);
  const resolutionMutation = useResolutionMutation(projectId, queryClient, notifySuccess);
  const recheckMutation = useRecheckMutation(projectId, queryClient, notifySuccess);
  const [pendingItemIds, setPendingItemIds] = useState<ReadonlySet<string>>(new Set());
  const [itemErrors, setItemErrors] = useState<ReadonlySet<string>>(new Set());
  const resolveCoverage = useCallback(async (input: CoverageResolutionInput) => {
    setPendingItemIds((current) => new Set(current).add(input.assessmentId));
    setItemErrors((current) => withoutId(current, input.assessmentId));
    try {
      return await resolutionMutation.mutateAsync(input);
    } catch (error) {
      setItemErrors((current) => new Set(current).add(input.assessmentId));
      throw error;
    } finally {
      setPendingItemIds((current) => withoutId(current, input.assessmentId));
    }
  }, [resolutionMutation]);
  return {
    analyze: analysisMutation.mutateAsync,
    analysisMutation,
    initialize: initializationMutation.mutateAsync,
    initializationMutation,
    resolveCoverage,
    resolutionMutation,
    recheckCoverage: recheckMutation.mutateAsync,
    recheckMutation,
    pendingItemIds,
    itemErrors,
    statusQuery,
  };
}

function withoutId(current: ReadonlySet<string>, id: string): ReadonlySet<string> {
  const next = new Set(current);
  next.delete(id);
  return next;
}
