"use client";

import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/common/components/ui/dialog";
import { SplitDbmlDiff } from "../../proposal-review/components/DbmlDiffViews";
import { diffLines } from "../../proposal-review/utils/dbml-text-diff";
import type { DraftRecoveryCandidate } from "../hooks/use-draft-recovery";

interface DraftRecoveryDialogProps {
  candidate: DraftRecoveryCandidate | null;
  onRestore: () => void;
  onDiscard: () => void;
}

/** So sánh server/local trước khi khôi phục draft hoặc giải quyết conflict. */
export function DraftRecoveryDialog(props: DraftRecoveryDialogProps) {
  const { t } = useTranslation("modeling-workspace");
  const diff = useMemo(
    () =>
      props.candidate
        ? diffLines(props.candidate.server.dbml, props.candidate.local.dbml)
        : [],
    [props.candidate],
  );

  return (
    <Dialog open={Boolean(props.candidate)}>
      <DialogContent
        showCloseButton={false}
        className="flex h-[85vh] max-h-[85vh] w-[95vw] sm:max-w-6xl max-w-6xl flex-col p-6 rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-2xl dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100 overflow-hidden"
      >
        <DialogHeader className="shrink-0 gap-1.5">
          <DialogTitle className="text-base font-semibold text-slate-900 dark:text-slate-100">
            {t("TXT_RECOVERY_TITLE")}
          </DialogTitle>
          <DialogDescription className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            {t("TXT_RECOVERY_DESCRIPTION")}
          </DialogDescription>
        </DialogHeader>

        <div className="min-h-0 flex-1 flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-950 shadow-inner">
          <SplitDbmlDiff
            diff={diff}
            currentLabel={t("TXT_SERVER_DBML")}
            proposedLabel={t("TXT_LOCAL_DBML")}
          />
        </div>

        <DialogFooter className="shrink-0 mt-4 flex items-center justify-end gap-2.5 bg-transparent border-0 -mx-0 -mb-0 p-0 sm:justify-end">
          <Button
            variant="outline"
            onClick={props.onDiscard}
            className="border-slate-300 bg-white text-slate-700 hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 dark:hover:text-white"
          >
            {t("BTN_DISCARD_LOCAL")}
          </Button>
          <Button
            onClick={props.onRestore}
            className="bg-blue-600 font-semibold text-white hover:bg-blue-500 dark:bg-sky-600 dark:hover:bg-sky-500"
          >
            {t("BTN_RESTORE_DRAFT")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
