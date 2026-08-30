import type {
  AnswerClarificationRequest,
  ClarificationTurnResponse,
  ConfirmationTurnResponse,
  CancelledTurnResponse,
  ClarificationQuestionResponse,
  NoChangeTurnResponse,
  ProjectSessionResponse,
  ProposalTurnResponse,
  ToolResultTurnResponse,
  SessionEventResponse,
} from "@/api";
import {
  answerProjectSessionClarification,
  apiClient,
  createProjectSession,
  getPendingProjectSessionAction,
  decideProjectSessionPendingAction,
  listProjectSessionEvents,
  listProjectSessions,
  renameProjectSession,
  requireApiData,
  sendProjectSessionMessage,
  unwrapApiData,
} from "@/api";

export type AgentTurn =
  | ClarificationTurnResponse
  | ConfirmationTurnResponse
  | NoChangeTurnResponse
  | ProposalTurnResponse
  | ToolResultTurnResponse
  | CancelledTurnResponse;

export async function requestAgentSessions(
  projectId: string,
): Promise<ProjectSessionResponse[]> {
  const response = await listProjectSessions({
    client: apiClient,
    path: { project_id: projectId },
    query: { purpose: "DATA_MODELING" },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestPendingClarification(
  sessionId: string,
): Promise<ClarificationQuestionResponse | null> {
  const response = await getPendingProjectSessionAction({
    client: apiClient,
    path: { session_id: sessionId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return unwrapApiData(response.data);
}

export async function requestClarificationAnswer(
  sessionId: string,
  questionId: string,
  answer: AnswerClarificationRequest,
  isToolAction = false,
): Promise<AgentTurn> {
  const request = isToolAction
    ? decideProjectSessionPendingAction
    : answerProjectSessionClarification;
  const response = await request({
    body: answer,
    client: apiClient,
    path: { session_id: sessionId, question_id: questionId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestAgentSessionCreation(
  projectId: string,
): Promise<ProjectSessionResponse> {
  const response = await createProjectSession({
    body: { purpose: "DATA_MODELING" },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestSessionEvents(
  sessionId: string,
): Promise<SessionEventResponse[]> {
  const response = await listProjectSessionEvents({
    client: apiClient,
    path: { session_id: sessionId },
    query: { limit: 200, conversation_only: false },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestSessionMessage(
  sessionId: string,
  content: string,
  clientMessageId: string,
  locale: "vi" | "en",
): Promise<AgentTurn> {
  const response = await sendProjectSessionMessage({
    body: { content, client_message_id: clientMessageId, locale },
    client: apiClient,
    path: { session_id: sessionId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestSessionRename(
  sessionId: string,
  title: string,
): Promise<ProjectSessionResponse> {
  const response = await renameProjectSession({
    body: { title },
    client: apiClient,
    path: { session_id: sessionId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}
