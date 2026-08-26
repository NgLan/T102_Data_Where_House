"use client";

import { Bot, Loader2, User } from "lucide-react";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import type { SessionEventResponse } from "@/api";

interface RequirementChatMessagesProps {
  events: SessionEventResponse[];
  isSending: boolean;
}

/**
 * Danh sách tin nhắn trao đổi giữa Người dùng và Bot trong phiên làm rõ yêu cầu.
 *
 * @param props - Danh sách sự kiện và trạng thái gửi tin
 * @returns Component danh sách tin nhắn tự động cuộn xuống dưới cùng
 */
export function RequirementChatMessages(props: RequirementChatMessagesProps) {
  const { t } = useTranslation("project-init");
  const containerRef = useRef<HTMLDivElement>(null);

  const publicEvents = props.events.filter(
    (event) =>
      (event.role === "USER" || event.role === "AGENT") &&
      (event.type === "MESSAGE" || event.type === "ANSWER" || event.type === "QUESTION"),
  );

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [publicEvents.length, props.isSending]);

  return (
    <div ref={containerRef} className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
      {publicEvents.length === 0 && (
        <p className="py-10 text-center text-sm text-muted-foreground">
          {t("TXT_REQUIREMENT_CHAT_EMPTY")}
        </p>
      )}

      {publicEvents.map((event) => {
        const isUser = event.role === "USER";
        return (
          <article
            key={event.id}
            className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}
          >
            <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
              {isUser ? <User className="size-4" /> : <Bot className="size-4" />}
            </span>
            <p
              className={`max-w-[82%] whitespace-pre-wrap rounded-2xl border px-3.5 py-2.5 text-sm leading-relaxed ${
                isUser
                  ? "border-primary/20 bg-primary text-primary-foreground"
                  : "border-border bg-muted/40 text-foreground"
              }`}
            >
              {event.content}
            </p>
          </article>
        );
      })}

      {props.isSending && (
        <p className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin text-primary" />
          {t("MSG_REQUIREMENT_BOT_PROCESSING")}
        </p>
      )}
    </div>
  );
}
