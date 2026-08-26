import type {
  AnswerRequirementClarificationRequest,
  RequirementContinuationAction,
  RequirementClarificationResponse,
  SessionEventResponse,
} from "@/api";
import {
  analyzeProjectRequirementClarification,
  answerProjectRequirementClarification,
  apiClient,
  chooseProjectRequirementContinuation,
  deleteRequirement,
  getProjectRequirementClarification,
  listProjectSessionEvents,
  requireApiData,
  sendProjectRequirementClarificationMessage,
} from "@/api";

export async function requestRequirementClarification(
  projectId: string,
): Promise<RequirementClarificationResponse> {
  const response = await getProjectRequirementClarification({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Persist continuation gate action của current Requirement session. */
export async function requestRequirementContinuation(
  projectId: string,
  sessionId: string,
  expectedRevision: number,
  action: RequirementContinuationAction,
): Promise<RequirementClarificationResponse> {
  const response = await chooseProjectRequirementContinuation({
    body: { action, expected_revision: expectedRevision },
    client: apiClient,
    path: { project_id: projectId, session_id: sessionId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestRequirementAnalysis(
  projectId: string,
  expectedRevision: number,
): Promise<RequirementClarificationResponse> {
  const response = await analyzeProjectRequirementClarification({
    body: { expected_revision: expectedRevision },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

export async function requestRequirementAnswer(
  projectId: string,
  sessionId: string,
  questionId: string,
  answer: AnswerRequirementClarificationRequest,
): Promise<RequirementClarificationResponse> {
  const response = await answerProjectRequirementClarification({
    body: answer,
    client: apiClient,
    path: {
      project_id: projectId,
      session_id: sessionId,
      question_id: questionId,
    },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

export async function requestClarificationEvents(
  sessionId: string,
): Promise<SessionEventResponse[]> {
  const response = await listProjectSessionEvents({
    client: apiClient,
    path: { session_id: sessionId },
    query: { limit: 200, conversation_only: true },
    responseStyle: "fields",
    throwOnError: true,
    meta: { shouldNotify: false },
  });
  return requireApiData(response.data);
}

/** Gửi follow-up message khi session không còn pending question. */
export async function requestRequirementMessage(
  projectId: string,
  sessionId: string,
  expectedRevision: number,
  message: string,
): Promise<RequirementClarificationResponse> {
  const response = await sendProjectRequirementClarificationMessage({
    body: { expected_revision: expectedRevision, message },
    client: apiClient,
    path: { project_id: projectId, session_id: sessionId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Xóa một Structured Requirement khỏi kết quả hiện hành. */
export async function requestRequirementDelete(
  projectId: string,
  requirementId: string,
): Promise<void> {
  await deleteRequirement({
    client: apiClient,
    path: { project_id: projectId, requirement_id: requirementId },
    responseStyle: "fields",
    throwOnError: true,
  });
}
