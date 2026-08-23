"use client";

import { Bot, Columns3, PanelBottom, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectSessionResponse, SessionEventResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { useAppNotification } from "@/common/notifications";
import type { AgentDock } from "../hooks/use-agent-dock";
import { AgentEventList } from "./AgentEventList";
import { AgentSessionControls } from "./AgentSessionControls";
import { AgentMessageComposer } from "./AgentMessageComposer";

interface AgentSessionPanelProps {
  projectId: string;
  sessions: ProjectSessionResponse[];
  selectedSessionId: string | null;
  events: SessionEventResponse[];
  draft: string;
  isSending: boolean;
  canSend: boolean;
  errorCode: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDraftChange: (value: string) => void;
  onSend: () => void;
  onDockChange: (dock: AgentDock) => void;
  onRenameSession: (title: string) => void;
}

/** Panel hội thoại nhiều session với controls dock tương tự IDE. */
export function AgentSessionPanel(props: AgentSessionPanelProps) {
  const { t } = useTranslation("ai-chat");
  const { getErrorMessage } = useAppNotification();
  return (
    <section className="flex h-full min-h-0 flex-col bg-amber-50/40 text-slate-800 dark:bg-slate-950 dark:text-slate-200">
      <header className="flex items-center gap-2 border-b border-amber-200/80 bg-amber-100/50 px-3 py-2 dark:border-slate-800/80 dark:bg-slate-900/60">
        <div className="mr-auto flex min-w-0 items-center gap-2">
          <div className="flex size-6 shrink-0 items-center justify-center rounded-lg bg-amber-500/15 text-amber-700 ring-1 ring-amber-500/30 dark:bg-sky-500/10 dark:text-sky-400 dark:ring-sky-500/25">
            <Bot className="size-3.5" />
          </div>
          <strong className="truncate text-xs font-semibold tracking-tight text-slate-900 dark:text-slate-100">
            {t("TXT_AI_CHAT_TITLE")}
          </strong>
        </div>
        <div className="flex items-center gap-0.5">
          <Button
            size="icon-xs"
            variant="ghost"
            className="text-slate-600 hover:bg-amber-200/60 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            onClick={() => props.onDockChange("right")}
            aria-label={t("BTN_DOCK_RIGHT")}
          >
            <Columns3 className="size-3.5" />
          </Button>
          <Button
            size="icon-xs"
            variant="ghost"
            className="text-slate-600 hover:bg-amber-200/60 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            onClick={() => props.onDockChange("inspector-bottom")}
            aria-label={t("BTN_DOCK_BOTTOM")}
          >
            <PanelBottom className="size-3.5" />
          </Button>
          <Button
            size="icon-xs"
            variant="ghost"
            className="text-slate-600 hover:bg-amber-200/60 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            onClick={() => props.onDockChange("hidden")}
            aria-label={t("BTN_CLOSE_AGENT")}
          >
            <X className="size-3.5" />
          </Button>
        </div>
      </header>
      <AgentSessionControls {...props} />
      <AgentEventList
        events={props.events}
        isSending={props.isSending}
        projectId={props.projectId}
      />
      {props.errorCode && (
        <p role="alert" className="px-3 text-xs text-destructive">
          {getErrorMessage(props.errorCode)}
        </p>
      )}
      <AgentMessageComposer {...props} hasSession={Boolean(props.selectedSessionId)} />
    </section>
  );
}
