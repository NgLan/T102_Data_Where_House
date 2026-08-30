"use client";

import { CircleCheck, CircleX, Download } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { ChatEvent } from "../types/chat-event";
import { downloadToolArtifact } from "../services/tool-artifact-api";

export function AgentToolResultCard({ event }: { event: ChatEvent }) {
  const { t } = useTranslation("ai-chat");
  const [isDownloading, setIsDownloading] = useState(false);
  const succeeded = event.tool_status === "SUCCESS";
  const Icon = succeeded ? CircleCheck : CircleX;
  const download = async () => {
    if (!event.artifact_filename) return;
    setIsDownloading(true);
    try {
      await downloadToolArtifact({
        sessionId: event.session_id,
        toolResultEventId: event.id,
        filename: event.artifact_filename,
      });
    } finally {
      setIsDownloading(false);
    }
  };
  return (
    <article className={`rounded-xl border p-3 text-xs ${succeeded ? "border-emerald-500/30 bg-emerald-500/10" : "border-rose-500/30 bg-rose-500/10"}`}>
      <div className="flex items-center gap-2 font-semibold">
        <Icon className="size-4" />
        <span>{succeeded ? t("TXT_TOOL_SUCCESS") : t("TXT_TOOL_FAILED")}</span>
      </div>
      {event.executed_statements !== null && (
        <p className="mt-2 text-slate-600 dark:text-slate-300">
          {t("TXT_SANDBOX_RESULT", {
            succeeded: event.succeeded_statements ?? 0,
            total: event.executed_statements,
            duration: Math.round(event.total_duration_ms ?? 0),
          })}
        </p>
      )}
      {event.artifact_filename && (
        <button
          type="button"
          disabled={isDownloading}
          onClick={() => void download()}
          className="mt-2 inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-sky-500/40 px-2.5 py-1.5 font-semibold text-sky-600 dark:text-sky-300"
        >
          <Download className="size-3.5" />
          {isDownloading ? t("TXT_DOWNLOADING") : t("BTN_DOWNLOAD_ARTIFACT")}
        </button>
      )}
    </article>
  );
}
