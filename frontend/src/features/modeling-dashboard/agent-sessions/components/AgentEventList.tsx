"use client";

import {
  Bot,
  ChevronDown,
  ChevronUp,
  CircleDot,
  GitCompare,
  Loader2,
  User,
} from "lucide-react";
import { Fragment, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { ChangeProposalDetailResponse } from "@/api";
import type { ChatEvent } from "../types/chat-event";
import { fetchProposalDetail } from "../../modeling-workspace/components/proposal-review/services/proposal-api";
import { ChatProposalDiff } from "./ChatProposalDiff";
import { AgentToolResultCard } from "./AgentToolResultCard";

/** Timeline công khai của message và các mốc Agent/tool. */
export function AgentEventList({
  events,
  isSending,
  pendingClientMessageId = null,
  projectId,
}: {
  events: ChatEvent[];
  isSending: boolean;
  pendingClientMessageId?: string | null;
  projectId: string;
}) {
  const { t } = useTranslation("ai-chat");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [events.length, isSending]);

  return (
    <div className="dark-scrollbar min-h-0 flex-1 space-y-3.5 overflow-y-auto p-3.5">
      {events.length === 0 && !isSending && (
        <div className="flex h-32 flex-col items-center justify-center gap-2 text-center text-xs text-slate-500">
          <Bot className="size-6 text-slate-600" />
          <p>{t("TXT_SESSION_EMPTY")}</p>
        </div>
      )}
      {events.map((event) => (
        <AgentEvent key={event.id} event={event} projectId={projectId} />
      ))}
      {isSending && (
        <ThinkingIndicator text={t("MSG_AI_CHAT_THINKING")} />
      )}
      <div ref={endRef} />
    </div>
  );
}

function AgentEvent({
  event,
  projectId,
}: {
  event: ChatEvent;
  projectId: string;
}) {
  const { t } = useTranslation("ai-chat");
  const [isExpanded, setIsExpanded] = useState(false);
  const [proposal, setProposal] =
    useState<ChangeProposalDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const isUser = event.role === "USER";
  const isFailed = event.status === "FAILED";

  if (event.type === "AGENT_CALL")
    return <StatusEvent text={t("TXT_AGENT_STARTED")} />;
  if (event.type === "TOOL_CALL")
    return <StatusEvent text={t("TXT_TOOL_STARTED")} />;
  if (event.type === "TOOL_RESULT")
    return <AgentToolResultCard event={event} />;
  if (event.type === "AGENT_RESULT")
    return isFailed ? (
      <StatusEvent text={event.content ?? t("TXT_AGENT_COMPLETED")} />
    ) : null;

  const handleToggleProposal = async () => {
    if (isExpanded) {
      setIsExpanded(false);
      return;
    }
    if (!proposal && event.proposal_change_id) {
      setIsLoading(true);
      try {
        const detail = await fetchProposalDetail(
          projectId,
          event.proposal_change_id,
        );
        setProposal(detail);
        setIsExpanded(true);
      } catch {
        // error handling
      } finally {
        setIsLoading(false);
      }
    } else {
      setIsExpanded(true);
    }
  };

  return (
    <article
      className={`flex items-start gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <span
        className={`flex size-7 shrink-0 items-center justify-center rounded-full ring-1 ${
          isUser
            ? "bg-amber-200/70 text-amber-900 ring-amber-300 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700"
            : "bg-amber-500/20 text-amber-700 ring-amber-500/35 dark:bg-sky-500/15 dark:text-sky-400 dark:ring-sky-500/30"
        }`}
      >
        {isUser ? <User className="size-3.5" /> : <Bot className="size-4" />}
      </span>
      <div
        className={`rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed shadow-xs ${
          isExpanded ? "w-full min-w-0" : "max-w-[85%]"
        } ${
          isUser
            ? "rounded-tr-xs bg-amber-500 text-white dark:bg-sky-600"
            : isFailed
              ? "rounded-tl-xs border border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-800/60 dark:bg-rose-950/40 dark:text-rose-300"
              : "rounded-tl-xs border border-amber-200/80 bg-white text-slate-800 shadow-xs dark:border-slate-800/90 dark:bg-slate-900/90 dark:text-slate-200"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">
          {event.content ?? t("TXT_AGENT_COMPLETED")}
        </p>
        {event.deliveryStatus === "failed" && (
          <p className="mt-1 text-[10px] font-semibold text-rose-200">
            {t("TXT_MESSAGE_SEND_FAILED")}
          </p>
        )}
        {event.proposal_change_id && (
          <div className="mt-2.5">
            <button
              type="button"
              onClick={() => void handleToggleProposal()}
              disabled={isLoading}
              className={`inline-flex cursor-pointer items-center gap-1.5 rounded-lg border px-2.5 py-1 text-[11px] font-semibold transition-all ${
                isExpanded
                  ? "border-emerald-500/60 bg-emerald-500/20 text-emerald-300 shadow-xs"
                  : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:border-emerald-500/60 hover:bg-emerald-500/20"
              }`}
            >
              {isLoading ? (
                <Loader2 className="size-3 animate-spin text-emerald-400" />
              ) : (
                <GitCompare className="size-3 text-emerald-400" />
              )}
              <span>{t("TXT_PROPOSAL_READY")}</span>
              {isExpanded ? (
                <ChevronUp className="size-3 text-emerald-400/80" />
              ) : (
                <ChevronDown className="size-3 text-emerald-400/80" />
              )}
            </button>
            {isExpanded && proposal && (
              <ChatProposalDiff proposal={proposal} />
            )}
          </div>
        )}
      </div>
    </article>
  );
}

function ThinkingIndicator({ text }: { text: string }) {
  return (
    <div className="flex w-fit items-center gap-2 rounded-xl border border-sky-500/20 bg-sky-500/10 px-3 py-2 text-xs font-medium text-sky-300">
      <Loader2 className="size-3.5 animate-spin text-sky-400" />
      <span>{text}</span>
    </div>
  );
}

function StatusEvent({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2 px-2 py-0.5 text-[11px] font-mono text-slate-400">
      <CircleDot className="size-3 text-sky-400/80 animate-pulse" />
      <span>{text}</span>
    </div>
  );
}
