"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  AnswerRequirementClarificationRequest,
  RequirementClarificationResponse,
  RequirementContinuationAction,
} from "@/api";
import { projectInitQueryKeys } from "../../../constants/project-init-query-keys";
import {
  requestClarificationEvents,
  requestRequirementAnalysis,
  requestRequirementAnswer,
  requestRequirementClarification,
  requestRequirementContinuation,
  requestRequirementDelete,
  requestRequirementMessage,
} from "../services/requirement-clarification-api";
import { createRequirementTurnDiff } from "../requirement-turn-diff";

/** Query/mutations của current Requirement clarification cycle. */
export function useRequirementClarification(projectId: string) {
  const queryClient = useQueryClient();
  const [turnDiff, setTurnDiff] = useState<ReturnType<typeof createRequirementTurnDiff>>();
  const stateQuery = useQuery({
    queryKey: projectInitQueryKeys.clarification(projectId),
    queryFn: () => requestRequirementClarification(projectId),
  });
  const sessionId = stateQuery.data?.session?.id ?? null;
  const eventsQuery = useQuery({
    queryKey: projectInitQueryKeys.clarificationEvents(sessionId),
    queryFn: () => requestClarificationEvents(sessionId as string),
    enabled: Boolean(sessionId),
  });
  const refreshEvents = async () => {
    await queryClient.invalidateQueries({
      queryKey: projectInitQueryKeys.clarificationEvents(sessionId),
    });
  };
  const applyTurnState = async (state: RequirementClarificationResponse) => {
    const previous = queryClient.getQueryData<RequirementClarificationResponse>(
      projectInitQueryKeys.clarification(projectId),
    );
    setTurnDiff(createRequirementTurnDiff(previous?.requirements ?? [], state.requirements));
    queryClient.setQueryData(projectInitQueryKeys.clarification(projectId), state);
    await refreshEvents();
  };
  const analyzeMutation = useMutation({
    mutationKey: ["analyze-requirement", projectId],
    mutationFn: (revision: number) =>
      requestRequirementAnalysis(projectId, revision),
    onSuccess: applyTurnState,
  });
  const answerMutation = useMutation({
    mutationKey: ["answer-requirement", projectId],
    mutationFn: (answer: AnswerRequirementClarificationRequest) => {
      const pending = stateQuery.data?.pending_question;
      if (!sessionId || !pending) throw new Error("NO_PENDING_CLARIFICATION");
      return requestRequirementAnswer(
        projectId,
        sessionId,
        pending.question_id,
        answer,
      );
    },
    onSuccess: applyTurnState,
  });
  const messageMutation = useMutation({
    mutationKey: ["message-requirement", projectId],
    mutationFn: (message: string) => {
      const state = stateQuery.data;
      if (!state?.session) throw new Error("NO_REQUIREMENT_SESSION");
      return requestRequirementMessage(
        projectId, state.session.id, state.requirement_revision, message,
      );
    },
    onSuccess: applyTurnState,
  });
  const continuationMutation = useMutation({
    mutationKey: ["requirement-continuation", projectId],
    mutationFn: (action: RequirementContinuationAction) => {
      const state = stateQuery.data;
      if (!state?.session) throw new Error("NO_REQUIREMENT_SESSION");
      return requestRequirementContinuation(
        projectId, state.session.id, state.requirement_revision, action,
      );
    },
    onSuccess: (state) => {
      queryClient.setQueryData(projectInitQueryKeys.clarification(projectId), state);
    },
  });
  const deleteMutation = useMutation({
    mutationKey: ["delete-structured-requirement", projectId],
    mutationFn: (requirementId: string) =>
      requestRequirementDelete(projectId, requirementId),
    onSuccess: async (_, requirementId) => {
      const deleted = stateQuery.data?.requirements.find(
        (item) => item.id === requirementId,
      );
      setTurnDiff({ newIds: [], changedIds: [], deletedTitles: deleted ? [deleted.title] : [] });
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.clarification(projectId),
        }),
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.project(projectId),
        }),
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.sources(projectId),
        }),
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.status(projectId),
        }),
      ]);
    },
  });
  return {
    stateQuery,
    eventsQuery,
    analyze: analyzeMutation.mutateAsync,
    answer: answerMutation.mutateAsync,
    sendMessage: messageMutation.mutateAsync,
    chooseContinuation: continuationMutation.mutateAsync,
    deleteRequirement: deleteMutation.mutateAsync,
    isProcessing:
      analyzeMutation.isPending ||
      answerMutation.isPending ||
      messageMutation.isPending ||
      continuationMutation.isPending ||
      deleteMutation.isPending,
    analyzeMutation,
    answerMutation,
    messageMutation,
    continuationMutation,
    deleteMutation,
    turnDiff,
  };
}
