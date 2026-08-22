"use client";

import { useCallback, useEffect, useState } from "react";
import {
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
  requestSessionEvents,
  requestSessionMessage,
  requestSessionRename,
} from "../services/agent-session-api";

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
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
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
    void requestSessionEvents(selectedSessionId).then((history) => {
      setEvents(history);
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
    setSelectedSessionId(sessionId);
  }, []);

  const createSession = useCallback(async () => {
    const created = await requestAgentSessionCreation(options.projectId);
    setSessions((current) => [created, ...current]);
    selectSession(created.id);
  }, [options.projectId, selectSession]);
  const send = useCallback(async () => {
    const content = draft.trim();
    if (!selectedSessionId || !content || isSending) return;
    setIsSending(true);
    try {
      if (!(await options.ensureLatestModel())) return;
      setDraft("");
      const turn = await requestSessionMessage(selectedSessionId, content);
      const history = await requestSessionEvents(selectedSessionId);
      setEvents(history);
      if (turn.kind === "proposal") {
        options.onProposal(
          await fetchProposalDetail(options.projectId, turn.proposal_change_id),
        );
      }
      setErrorCode(null);
    } catch (error: unknown) {
      setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
    } finally {
      setIsSending(false);
    }
  }, [draft, isSending, options, selectedSessionId]);
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
    draft,
    isSending,
    errorCode,
    canSend: Boolean(selectedSessionId && draft.trim() && !isSending),
    selectSession,
    setDraft,
    createSession,
    send,
    selectedProposal,
    openProposal,
    renameSession,
  };
}
