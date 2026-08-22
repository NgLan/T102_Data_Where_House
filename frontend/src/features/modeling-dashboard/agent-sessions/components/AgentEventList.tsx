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
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { ChangeProposalDetailResponse, SessionEventResponse } from "@/api";
import { fetchProposalDetail } from "../../modeling-workspace/components/proposal-review/services/proposal-api";
import { ChatProposalDiff } from "./ChatProposalDiff";

/** Timeline công khai của message và các mốc Agent/tool. */
export function AgentEventList({
  events,
  isSending,
  projectId,
}: {
  events: SessionEventResponse[];
  isSending: boolean;
  projectId: string;
}) {
  const { t } = useTranslation("ai-chat");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [events.length, isSending]);

  return (
    <div className="dark-scrollbar min-h-0 flex-1 space-y-3.5 overflow-y-auto p-3.5">
      {events.length === 0 && (
        <div className="flex h-32 flex-col items-center justify-center gap-2 text-center text-xs text-slate-500">
          <Bot className="size-6 text-slate-600" />
          <p>{t("TXT_SESSION_EMPTY")}</p>
        </div>
      )}
      {events.map((event) => (
        <AgentEvent key={event.id} event={event} projectId={projectId} />
      ))}
      {isSending && (
        <div className="flex items-center gap-2 rounded-xl border border-sky-500/20 bg-sky-500/10 px-3 py-2 text-xs font-medium text-sky-300 w-fit">
          <Loader2 className="size-3.5 animate-spin text-sky-400" />
          <span>{t("MSG_AI_CHAT_THINKING")}</span>
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}

function AgentEvent({
  event,
  projectId,
}: {
  event: SessionEventResponse;
  projectId: string;
}) {
  const { t } = useTranslation("ai-chat");
  const [isExpanded, setIsExpanded] = useState(false);
  const [proposal, setProposal] =
    useState<ChangeProposalDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (event.type === "AGENT_CALL")
    return <StatusEvent text={t("TXT_AGENT_STARTED")} />;
  if (event.type === "TOOL_CALL")
    return <StatusEvent text={t("TXT_TOOL_STARTED")} />;
  if (event.type === "TOOL_RESULT")
    return <StatusEvent text={t("TXT_TOOL_COMPLETED")} />;

  const isUser = event.role === "USER";
  const isFailed = event.status === "FAILED";

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
            ? "bg-slate-800 text-slate-300 ring-slate-700"
            : "bg-sky-500/15 text-sky-400 ring-sky-500/30"
        }`}
      >
        {isUser ? <User className="size-3.5" /> : <Bot className="size-4" />}
      </span>
      <div
        className={`rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed shadow-xs ${
          isExpanded ? "w-full min-w-0" : "max-w-[85%]"
        } ${
          isUser
            ? "rounded-tr-xs bg-sky-600 text-white"
            : isFailed
              ? "rounded-tl-xs border border-rose-800/60 bg-rose-950/40 text-rose-300"
              : "rounded-tl-xs border border-slate-800/90 bg-slate-900/90 text-slate-200"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">
          {event.content ?? t("TXT_AGENT_COMPLETED")}
        </p>
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

function StatusEvent({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2 px-2 py-0.5 text-[11px] font-mono text-slate-400">
      <CircleDot className="size-3 text-sky-400/80 animate-pulse" />
      <span>{text}</span>
    </div>
  );
}
