"use client";

import Link from "next/link";
import {
  ArrowLeft,
  CloudOff,
  PanelRightClose,
  PanelRightOpen,
  Rocket,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { createWorkflowHref } from "@/common/routing/workflow-routing";
import type { WorkspaceStatus } from "../types/modeling-workspace-types";
import { ReloadSnapshotButton } from "./ReloadSnapshotButton";
import { SaveDataModelButton } from "./SaveDataModelButton";

interface ModelingWorkspaceHeaderProps {
  canSave: boolean;
  errorMessage: string | null;
  hasProject: boolean;
  isDirty: boolean;
  isInspectorOpen: boolean;
  status: WorkspaceStatus;
  onReload: () => void;
  onSave: () => void;
  onToggleInspector: () => void;
}

/** Hiển thị điều hướng và các action toàn cục của Modeling Workspace. */
export function ModelingWorkspaceHeader(props: ModelingWorkspaceHeaderProps) {
  const { t } = useTranslation("modeling-dashboard");
  return (
    <header className="flex flex-wrap items-center gap-2 border-b bg-white px-3 py-2">
      <Button asChild variant="outline" size="sm">
        <Link href={createWorkflowHref("project-init")}>
          <ArrowLeft />
          {t("BTN_RECONFIGURE")}
        </Link>
      </Button>
      <h2 className="mr-auto text-sm font-semibold text-slate-900">
        {t("TXT_TITLE")}
      </h2>
      {!props.hasProject && <LocalDraftLabel />}
      {props.errorMessage && (
        <span className="text-xs text-red-600" role="alert">
          {props.errorMessage}
        </span>
      )}
      <InspectorToggle {...props} />
      <ReloadSnapshotButton
        isDirty={props.isDirty}
        isDisabled={!props.hasProject || props.status === "loading"}
        onReload={props.onReload}
      />
      <SaveDataModelButton
        canSave={props.canSave}
        isDirty={props.isDirty}
        status={props.status}
        onSave={props.onSave}
      />
      <Button asChild size="sm">
        <Link href={createWorkflowHref("sandbox")}>
          <Rocket />
          {t("BTN_RUN_SANDBOX")}
        </Link>
      </Button>
    </header>
  );
}

/** Hiển thị cảnh báo khi workspace chỉ có draft local. */
function LocalDraftLabel() {
  const { t } = useTranslation("modeling-dashboard");
  return (
    <span className="flex items-center gap-1 text-xs text-amber-700">
      <CloudOff className="size-3.5" />
      {t("MSG_LOCAL_ONLY")}
    </span>
  );
}

/** Bật hoặc tắt inspector mà vẫn giữ selection hiện tại. */
function InspectorToggle(props: ModelingWorkspaceHeaderProps) {
  const { t } = useTranslation("modeling-dashboard");
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
