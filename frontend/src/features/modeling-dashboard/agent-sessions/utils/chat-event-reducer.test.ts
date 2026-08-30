import { describe, expect, it } from "vitest";
import type { SessionEventResponse } from "@/api";
import {
  createOptimisticUserEvent,
  markChatEventFailed,
  mergeChatEvents,
} from "./chat-event-reducer";

function serverUserEvent(input: {
  id: string;
  clientMessageId: string;
  content?: string;
}): SessionEventResponse {
  return {
    id: input.id,
    session_id: "session-1",
    turn_id: "turn-1",
    role: "USER",
    type: "MESSAGE",
    content: input.content ?? "Xuất tài liệu phân tích",
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
    created_at: "2026-08-28T00:00:00Z",
  };
}

describe("chat-event-reducer", () => {
  it("replaces an optimistic event using client_message_id", () => {
    const optimistic = createOptimisticUserEvent({
      sessionId: "session-1",
      clientMessageId: "client-1",
      content: "Xuất tài liệu phân tích",
    });
    const serverEvent = serverUserEvent({
      id: "event-1",
      clientMessageId: "client-1",
    });

    const merged = mergeChatEvents([optimistic], [serverEvent]);

    expect(merged).toEqual([serverEvent]);
    expect(merged[0].id).toBe("event-1");
    expect(merged[0].deliveryStatus).toBeUndefined();
  });

  it("does not deduplicate messages by matching text", () => {
    const first = serverUserEvent({
      id: "event-1",
      clientMessageId: "client-1",
      content: "Nội dung giống nhau",
    });
    const second = serverUserEvent({
      id: "event-2",
      clientMessageId: "client-2",
      content: "Nội dung giống nhau",
    });

    const merged = mergeChatEvents([first], [second]);

    expect(merged).toHaveLength(2);
    expect(merged.map((event) => event.id)).toEqual(["event-1", "event-2"]);
  });

  it("retains the optimistic event and marks it failed", () => {
    const optimistic = createOptimisticUserEvent({
      sessionId: "session-1",
      clientMessageId: "client-1",
      content: "Chạy sandbox",
    });

    const failed = markChatEventFailed([optimistic], "client-1");

    expect(failed).toHaveLength(1);
    expect(failed[0]).toMatchObject({
      id: optimistic.id,
      client_message_id: "client-1",
      deliveryStatus: "failed",
    });
  });
});
