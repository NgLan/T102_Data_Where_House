"use client";

import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import type {
  AnswerClarificationRequest,
  ChangeProposalDetailResponse,
  ClarificationQuestionResponse,
} from "@/api";
import { handleApiError } from "@/api";
import { fetchProposalDetail } from "../../modeling-workspace/components/proposal-review/services/proposal-api";
import {
  type AgentTurn,
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
  onOptimisticMessage: (input: {
    sessionId: string;
    clientMessageId: string;
    content: string;
  }) => void;
  onMessageFailed: (clientMessageId: string) => void;
}

/** Điều phối hai command bắt đầu và resume Agent turn. */
export function useAgentTurnActions(options: AgentTurnActionsOptions) {
  const { i18n } = useTranslation();
  const {
    ensureLatestModel,
    onProposal,
    pendingClarification,
    projectId,
    refreshSession,
    selectedSessionId,
  } = options;
  const language = i18n?.resolvedLanguage;
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [pendingClientMessageId, setPendingClientMessageId] =
    useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const handleTurn = useCallback(
    async (
      turn: AgentTurn,
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
    const clientMessageId = crypto.randomUUID();
    options.onOptimisticMessage({ sessionId, clientMessageId, content });
    setDraft("");
    setPendingClientMessageId(clientMessageId);
    setIsSending(true);
    try {
      if (!(await ensureLatestModel())) {
        options.onMessageFailed(clientMessageId);
        return;
      }
      const locale = language?.startsWith("en") ? "en" : "vi";
      const turn = await requestSessionMessage(
        sessionId,
        content,
        clientMessageId,
        locale,
      );
      await refreshSession(sessionId);
      await handleTurn(turn);
      setErrorCode(null);
    } catch (error: unknown) {
      options.onMessageFailed(clientMessageId);
      setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
    } finally {
      setIsSending(false);
      setPendingClientMessageId(null);
    }
  }, [draft, ensureLatestModel, handleTurn, isSending, language, options, refreshSession, selectedSessionId]);

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
          pending.question_kind !== "CLARIFICATION",
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
    pendingClientMessageId,
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
