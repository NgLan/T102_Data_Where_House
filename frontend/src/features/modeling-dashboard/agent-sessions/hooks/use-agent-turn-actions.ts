"use client";

import { useCallback, useState } from "react";
import type {
  AnswerClarificationRequest,
  ChangeProposalDetailResponse,
  ClarificationQuestionResponse,
  ClarificationTurnResponse,
  NoChangeTurnResponse,
  ProposalTurnResponse,
} from "@/api";
import { handleApiError } from "@/api";
import { fetchProposalDetail } from "../../modeling-workspace/components/proposal-review/services/proposal-api";
import {
  requestClarificationAnswer,
  requestSessionMessage,
} from "../services/agent-session-api";

interface AgentTurnActionsOptions {
  projectId: string;
  selectedSessionId: string | null;
  pendingClarification: ClarificationQuestionResponse | null;
  ensureLatestModel: () => Promise<boolean>;
  onProposal: (proposal: ChangeProposalDetailResponse) => void;
  refreshSession: (sessionId: string) => Promise<void>;
}

/** Điều phối hai command bắt đầu và resume Agent turn. */
export function useAgentTurnActions(options: AgentTurnActionsOptions) {
  const {
    ensureLatestModel,
    onProposal,
    pendingClarification,
    projectId,
    refreshSession,
    selectedSessionId,
  } = options;
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const handleTurn = useCallback(
    async (
      turn:
        | ClarificationTurnResponse
        | NoChangeTurnResponse
        | ProposalTurnResponse,
    ) => {
      if (turn.kind !== "proposal") return;
      onProposal(
        await fetchProposalDetail(projectId, turn.proposal_change_id),
      );
    },
    [onProposal, projectId],
  );

  const send = useCallback(async () => {
    const sessionId = selectedSessionId;
    const content = draft.trim();
    if (!sessionId || !content || isSending) return;
    setIsSending(true);
    try {
      if (!(await ensureLatestModel())) return;
      setDraft("");
      const turn = await requestSessionMessage(sessionId, content);
      await refreshSession(sessionId);
      await handleTurn(turn);
      setErrorCode(null);
    } catch (error: unknown) {
      setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
    } finally {
      setIsSending(false);
    }
  }, [draft, ensureLatestModel, handleTurn, isSending, refreshSession, selectedSessionId]);

  const answerClarification = useCallback(
    async (answer: AnswerClarificationRequest) => {
      const sessionId = selectedSessionId;
      const pending = pendingClarification;
      if (!sessionId || !pending || isSending) return;
      setIsSending(true);
      try {
        if (!(await ensureLatestModel())) return;
        const turn = await requestClarificationAnswer(
          sessionId,
          pending.question_id,
          answer,
        );
        await refreshSession(sessionId);
        await handleTurn(turn);
        setErrorCode(null);
      } catch (error: unknown) {
        setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
        await refreshSession(sessionId);
      } finally {
        setIsSending(false);
      }
    },
    [ensureLatestModel, handleTurn, isSending, pendingClarification, refreshSession, selectedSessionId],
  );

  return {
    draft,
    setDraft,
    isSending,
    errorCode,
    canSend: Boolean(
      selectedSessionId &&
        draft.trim() &&
        !isSending &&
        !pendingClarification,
    ),
    send,
    answerClarification,
  };
}
