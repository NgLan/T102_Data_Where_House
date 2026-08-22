import type {
  ClarificationTurnResponse,
  ProjectSessionResponse,
  ProposalTurnResponse,
  SessionEventResponse,
} from "@/api";
import {
  apiClient,
  createProjectSession,
  listProjectSessionEvents,
  listProjectSessions,
  renameProjectSession,
  requireApiData,
  sendProjectSessionMessage,
} from "@/api";

export async function requestAgentSessions(
  projectId: string,
): Promise<ProjectSessionResponse[]> {
  const response = await listProjectSessions({
    client: apiClient,
    path: { project_id: projectId },
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
    body: {},
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
    query: { limit: 200 },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestSessionMessage(
  sessionId: string,
  content: string,
): Promise<ClarificationTurnResponse | ProposalTurnResponse> {
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
