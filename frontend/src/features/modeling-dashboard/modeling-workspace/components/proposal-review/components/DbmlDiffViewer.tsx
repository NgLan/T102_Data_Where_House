"use client";

import { useState, type ReactNode } from "react";
import { AlertTriangle, GitCompare } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ChangeProposalDetailResponse } from "@/api";
import type { DiffLine } from "../utils/dbml-text-diff";
import { DbmlDiffHeader, type DiffViewMode } from "./DbmlDiffHeader";
import { SplitDbmlDiff, UnifiedDbmlDiff } from "./DbmlDiffViews";

export interface DbmlDiffViewerProps {
  proposal: ChangeProposalDetailResponse | null;
  diff: DiffLine[];
  addedCount: number;
  removedCount: number;
  hasDiff: boolean;
  submitErrorCode?: string | null;
}

/** Hiển thị thay đổi DBML theo chế độ unified hoặc split để người dùng duyệt. */
export function DbmlDiffViewer(props: DbmlDiffViewerProps) {
  const { t } = useTranslation("proposal-review");
  const { t: tErrors } = useTranslation("errors");
  const [mode, setMode] = useState<DiffViewMode>("unified");

  const submitBanner = props.submitErrorCode ? (
    <WarningBanner>
      {tErrors(props.submitErrorCode, {
        defaultValue: tErrors("UNKNOWN_ERROR"),
      })}
    </WarningBanner>
  ) : null;

  if (!props.proposal) {
    return (
      <DiffShell>
        {submitBanner}
        <DiffPlaceholder />
      </DiffShell>
    );
  }

  return (
    <DiffShell>
      {submitBanner}
      <DbmlDiffHeader
        proposal={props.proposal}
        mode={mode}
        addedCount={props.addedCount}
        removedCount={props.removedCount}
        onModeChange={setMode}
      />
      {props.proposal.is_outdated && (
        <WarningBanner title={t("TXT_OUTDATED_TITLE")}>
          {t("MSG_OUTDATED_DESCRIPTION", {
            baseRevision: props.proposal.base_revision,
            currentRevision: props.proposal.current_revision,
          })}
        </WarningBanner>
      )}
      {!props.hasDiff && (
        <div className="border-b border-slate-200 bg-slate-100/50 px-3.5 py-2 text-[11px] text-slate-500 dark:border-slate-800 dark:bg-slate-900/40 dark:text-slate-400">
          {t("MSG_DIFF_NO_CHANGE")}
        </div>
      )}
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
        {mode === "unified" ? (
          <UnifiedDbmlDiff diff={props.diff} />
        ) : (
          <SplitDbmlDiff
            diff={props.diff}
            currentLabel={t("TXT_CURRENT_DBML")}
            proposedLabel={t("TXT_PROPOSED_DBML")}
          />
        )}
      </div>
    </DiffShell>
  );
}

function DiffShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      {children}
    </div>
  );
}

function WarningBanner(props: { title?: string; children: ReactNode }) {
  return (
    <div className="flex items-start gap-2 border-b border-rose-500/30 bg-rose-500/10 px-3.5 py-2.5 text-[11px] text-rose-700 dark:text-rose-300">
      <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
      <div>
        {props.title && <div className="font-bold">{props.title}</div>}
        <p>{props.children}</p>
      </div>
    </div>
  );
}

function DiffPlaceholder() {
  const { t } = useTranslation("proposal-review");
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center text-xs text-slate-500 dark:text-slate-400">
      <GitCompare className="size-4" />
      <span>{t("MSG_DIFF_EMPTY")}</span>
    </div>
  );
}
