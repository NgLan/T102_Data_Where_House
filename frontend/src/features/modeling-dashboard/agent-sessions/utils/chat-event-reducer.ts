import type { SessionEventResponse } from "@/api";
import type { ChatEvent } from "../types/chat-event";

export function mergeChatEvents(
  current: ChatEvent[],
  incoming: SessionEventResponse[],
): ChatEvent[] {
  return incoming.reduce(mergeChatEvent, current);
}

export function createOptimisticUserEvent(input: {
  sessionId: string;
  clientMessageId: string;
  content: string;
}): ChatEvent {
  return {
    id: `optimistic-${input.clientMessageId}`,
    session_id: input.sessionId,
    turn_id: null,
    role: "USER",
    type: "MESSAGE",
    content: input.content,
    status: null,
    proposal_change_id: null,
    question_options: [],
    allow_custom_answer: false,
    answer_to_question_id: null,
    client_message_id: input.clientMessageId,
    question_kind: null,
    tool_name: null,
    tool_status: null,
    artifact_id: null,
    artifact_filename: null,
    artifact_mime_type: null,
    sandbox_schema_name: null,
    sandbox_endpoint_risk: null,
    executed_statements: null,
    succeeded_statements: null,
    failed_statements: null,
    total_duration_ms: null,
    created_at: new Date().toISOString(),
    deliveryStatus: "sending",
  };
}

export function markChatEventFailed(
  current: ChatEvent[],
  clientMessageId: string,
): ChatEvent[] {
  return current.map((event) =>
    event.client_message_id === clientMessageId
      ? { ...event, deliveryStatus: "failed" }
      : event,
  );
}

function mergeChatEvent(
  current: ChatEvent[],
  incoming: SessionEventResponse,
): ChatEvent[] {
  const index = current.findIndex(
    (event) =>
      event.id === incoming.id ||
      Boolean(
        incoming.client_message_id &&
          event.client_message_id === incoming.client_message_id,
      ),
  );
  if (index < 0) return [...current, incoming];
  const next = [...current];
  next[index] = incoming;
  return next;
}
