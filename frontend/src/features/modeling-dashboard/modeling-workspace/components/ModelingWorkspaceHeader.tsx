"use client";

import {
  CloudOff,
  PanelRightClose,
  PanelRightOpen,
  Bot,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import type { WorkspaceStatus } from "../types/modeling-workspace-types";
import type { AutosaveState } from "./draft-persistence/hooks/use-draft-autosave";
interface ModelingWorkspaceHeaderProps {
  autosaveState: AutosaveState;
  errorMessage: string | null;
  hasProject: boolean;
  isDirty: boolean;
  isSaveBlocked: boolean;
  lastSavedAt: string | null;
  isInspectorOpen: boolean;
  status: WorkspaceStatus;
  onToggleInspector: () => void;
  isAgentOpen: boolean;
  onToggleAgent: () => void;
}

/** Hiển thị điều hướng và các action toàn cục của Modeling Workspace. */
export function ModelingWorkspaceHeader(props: ModelingWorkspaceHeaderProps) {
  const { t } = useTranslation("modeling-workspace");
  return (
    <header className="flex flex-wrap items-center gap-2 border-b bg-card px-3 py-2">
      <h2 className="mr-auto text-sm font-semibold text-foreground">
        {t("TXT_TITLE")}
      </h2>
      {!props.hasProject && <LocalDraftLabel />}
      {props.errorMessage && (
        <span className="text-xs text-red-600" role="alert">
          {props.errorMessage}
        </span>
      )}
      <span className="text-xs text-muted-foreground" role="status">
        {t(resolveAutosaveKey(props), {
          time: props.lastSavedAt
            ? new Intl.DateTimeFormat(undefined, {
                hour: "2-digit",
                minute: "2-digit",
              }).format(new Date(props.lastSavedAt))
            : "--:--",
        })}
      </span>
      <InspectorToggle {...props} />
      <AgentToggle {...props} />
    </header>
  );
}

function resolveAutosaveKey(props: ModelingWorkspaceHeaderProps) {
  if (props.status === "conflict") return "TXT_AUTOSAVE_CONFLICT";
  if (props.status === "saving" || props.autosaveState === "saving")
    return "TXT_AUTOSAVE_SAVING";
  if (props.autosaveState === "retrying") return "TXT_AUTOSAVE_RETRYING";
  if (props.isDirty && props.isSaveBlocked) return "TXT_AUTOSAVE_BLOCKED";
  if (props.isDirty) return "TXT_AUTOSAVE_SCHEDULED";
  return "TXT_AUTOSAVE_SAVED";
}

/** Hiển thị cảnh báo khi workspace chỉ có draft local. */
function LocalDraftLabel() {
  const { t } = useTranslation("modeling-workspace");
  return (
    <span className="flex items-center gap-1 text-xs text-amber-700">
      <CloudOff className="size-3.5" />
      {t("MSG_LOCAL_ONLY")}
    </span>
  );
}

/** Bật hoặc tắt inspector mà vẫn giữ selection hiện tại. */
function InspectorToggle(props: ModelingWorkspaceHeaderProps) {
  const { t } = useTranslation("modeling-workspace");
  const key = props.isInspectorOpen
    ? "BTN_HIDE_INSPECTOR"
    : "BTN_SHOW_INSPECTOR";
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      aria-label={t(key)}
      onClick={props.onToggleInspector}
    >
      {props.isInspectorOpen ? <PanelRightClose /> : <PanelRightOpen />}
      {t(key)}
    </Button>
  );
}

/** Bật hoặc tắt panel AI Agent. */
function AgentToggle(props: ModelingWorkspaceHeaderProps) {
  const { t } = useTranslation("modeling-workspace");
  const key = props.isAgentOpen ? "BTN_HIDE_AGENT" : "BTN_SHOW_AGENT";
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      aria-label={t(key)}
      onClick={props.onToggleAgent}
    >
      <Bot className="size-4" />
      {t(key)}
    </Button>
  );
}
