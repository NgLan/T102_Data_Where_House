import { createEventSource, type EventSourceClient } from "eventsource-client";
import { zSessionEventResponse, type SessionEventResponse } from "@/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001/api/v1";

interface AgentEventStreamOptions {
  sessionId: string;
  lastEventId?: string;
  onEvent: (event: SessionEventResponse) => void;
}

/** Mở SSE có reconnect và Last-Event-ID do thư viện quản lý. */
export function openAgentEventStream(options: AgentEventStreamOptions): EventSourceClient {
  return createEventSource({
    url: `${API_BASE_URL}/sessions/${options.sessionId}/events/stream`,
    initialLastEventId: options.lastEventId,
    headers: { Accept: "text/event-stream" },
    credentials: "include",
    onMessage: (message) => {
      if (message.event !== "session.event") return;
      const parsed = zSessionEventResponse.safeParse(JSON.parse(message.data));
      if (parsed.success) options.onEvent(parsed.data);
    },
  });
}
