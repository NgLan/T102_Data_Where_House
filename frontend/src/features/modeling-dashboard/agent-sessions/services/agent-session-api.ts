import type {
  AnswerClarificationRequest,
  ClarificationTurnResponse,
  ClarificationQuestionResponse,
  NoChangeTurnResponse,
  ProjectSessionResponse,
  ProposalTurnResponse,
  SessionEventResponse,
} from "@/api";
import {
  answerProjectSessionClarification,
  apiClient,
  createProjectSession,
  getPendingProjectSessionClarification,
  listProjectSessionEvents,
  listProjectSessions,
  renameProjectSession,
  requireApiData,
  sendProjectSessionMessage,
  unwrapApiData,
} from "@/api";

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
  const response = await getPendingProjectSessionClarification({
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
): Promise<
  ClarificationTurnResponse | NoChangeTurnResponse | ProposalTurnResponse
> {
  const response = await answerProjectSessionClarification({
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
): Promise<
  ClarificationTurnResponse | NoChangeTurnResponse | ProposalTurnResponse
> {
  const response = await sendProjectSessionMessage({
    body: { content },
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
