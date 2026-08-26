"use client";

import { useCallback, useEffect, useState } from "react";
import {
  type ClarificationQuestionResponse,
  handleApiError,
  type ChangeProposalDetailResponse,
  type ProjectSessionResponse,
  type SessionEventResponse,
} from "@/api";
import { fetchProposalDetail } from "../../modeling-workspace/components/proposal-review/services/proposal-api";
import { openAgentEventStream } from "../services/agent-event-stream";
import {
  requestAgentSessionCreation,
  requestAgentSessions,
  requestPendingClarification,
  requestSessionEvents,
  requestSessionRename,
} from "../services/agent-session-api";
import { useAgentTurnActions } from "./use-agent-turn-actions";

interface AgentSessionsOptions {
  projectId: string;
  onProposal: (proposal: ChangeProposalDetailResponse) => void;
  ensureLatestModel: () => Promise<boolean>;
  onInspectProposal: () => void;
}

/** Quản lý session đã persist, history và SSE events của Agent. */
export function useAgentSessions(options: AgentSessionsOptions) {
  const [sessions, setSessions] = useState<ProjectSessionResponse[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    null,
  );
  const [events, setEvents] = useState<SessionEventResponse[]>([]);
  const [pendingClarification, setPendingClarification] =
    useState<ClarificationQuestionResponse | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [selectedProposal, setSelectedProposal] =
    useState<ChangeProposalDetailResponse | null>(null);

  const appendEvent = useCallback((event: SessionEventResponse) => {
    setEvents((current) =>
      current.some((item) => item.id === event.id)
        ? current
        : [...current, event],
    );
  }, []);
  const loadSessions = useCallback(async () => {
    try {
      setSessions(await requestAgentSessions(options.projectId));
    } catch (error: unknown) {
      setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
    }
  }, [options.projectId]);
  useEffect(() => {
    void Promise.resolve().then(loadSessions);
  }, [loadSessions]);
  useEffect(() => {
    if (!selectedSessionId) return;
    let stream: ReturnType<typeof openAgentEventStream> | null = null;
    void Promise.all([
      requestSessionEvents(selectedSessionId),
      requestPendingClarification(selectedSessionId),
    ]).then(([history, clarification]) => {
      setEvents(history);
      setPendingClarification(clarification);
      stream = openAgentEventStream({
        sessionId: selectedSessionId,
        lastEventId: history.at(-1)?.id,
        onEvent: appendEvent,
      });
    });
    return () => stream?.close();
  }, [appendEvent, selectedSessionId]);

  const selectSession = useCallback((sessionId: string) => {
    setEvents([]);
    setPendingClarification(null);
    setSelectedSessionId(sessionId);
  }, []);

  const createSession = useCallback(async () => {
    const created = await requestAgentSessionCreation(options.projectId);
    setSessions((current) => [created, ...current]);
    selectSession(created.id);
  }, [options.projectId, selectSession]);
  const refreshSession = useCallback(async (sessionId: string) => {
    const [history, clarification] = await Promise.all([
      requestSessionEvents(sessionId),
      requestPendingClarification(sessionId),
    ]);
    setEvents(history);
    setPendingClarification(clarification);
  }, []);
  const actions = useAgentTurnActions({
    projectId: options.projectId,
    selectedSessionId,
    pendingClarification,
    ensureLatestModel: options.ensureLatestModel,
    onProposal: options.onProposal,
    refreshSession,
  });
  const openProposal = useCallback(async (changeId: string) => {
    options.onInspectProposal();
    setSelectedProposal(await fetchProposalDetail(options.projectId, changeId));
  }, [options]);
  const renameSession = useCallback(async (title: string) => {
    if (!selectedSessionId) return;
    const renamed = await requestSessionRename(selectedSessionId, title);
    setSessions((current) => current.map((item) =>
      item.id === renamed.id ? renamed : item));
  }, [selectedSessionId]);
  return {
    sessions,
    selectedSessionId,
    events,
    pendingClarification,
    draft: actions.draft,
    isSending: actions.isSending,
    errorCode: actions.errorCode ?? errorCode,
    canSend: actions.canSend,
    selectSession,
    setDraft: actions.setDraft,
    createSession,
    send: actions.send,
    answerClarification: actions.answerClarification,
    selectedProposal,
    openProposal,
    renameSession,
  };
}
