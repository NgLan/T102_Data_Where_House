"use client";

import { ShieldCheck, XCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DataModelValidationIssueResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { useAppNotification } from "@/common/notifications";
import { ValidationIssueList } from "./ValidationIssueList";

interface ValidationPopupProps {
  issues: DataModelValidationIssueResponse[];
  errorCode: string | null;
  isTop: boolean;
  isDragging: boolean;
  dragHandlers: {
    onPointerDown: (e: React.PointerEvent) => void;
    onPointerMove: (e: React.PointerEvent) => void;
    onPointerUp: (e: React.PointerEvent) => void;
  };
  onClose: () => void;
  onSelectTable: (tableName: string) => void;
}

export function ValidationPopup({
  issues,
  errorCode,
  isTop,
  isDragging,
  dragHandlers,
  onClose,
  onSelectTable,
}: ValidationPopupProps) {
  const { t } = useTranslation("modeling-workspace");
  const { getErrorMessage } = useAppNotification();

  const errors = issues.filter((item) => item.severity === "ERROR");
  const warnings = issues.filter((item) => item.severity === "WARNING");

  return (
    <section
      className={`pointer-events-auto ${
        isTop ? "mt-3" : "mb-3"
      } flex max-h-[480px] w-96 max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white/95 text-slate-900 shadow-2xl backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/95 dark:text-slate-100 ${
        isDragging ? "pointer-events-none opacity-80" : ""
      }`}
    >
      <header
        {...dragHandlers}
        className="flex cursor-grab active:cursor-grabbing select-none touch-none items-center gap-2 border-b border-slate-200 bg-slate-50/80 px-4 py-3 dark:border-slate-800 dark:bg-slate-950/60"
      >
        <div className="flex size-6 items-center justify-center rounded-lg bg-amber-500/15 text-amber-600 ring-1 ring-amber-500/30 dark:bg-sky-500/10 dark:text-sky-400 dark:ring-sky-500/25">
          <ShieldCheck className="size-3.5" />
        </div>
        <strong className="mr-auto text-xs font-semibold text-slate-900 dark:text-slate-100">
          {t("TXT_VALIDATION_ENGINE")}
        </strong>
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
          className="text-slate-500 hover:bg-slate-200 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          aria-label={t("BTN_CLOSE_VALIDATION")}
        >
          <XCircle className="size-4" />
        </Button>
      </header>
      <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50/50 px-3.5 py-2 text-xs dark:border-slate-800 dark:bg-slate-950/30">
        <span className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-rose-50 px-2.5 py-0.5 font-semibold text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/15 dark:text-rose-300">
          {t("TXT_ERROR_COUNT", { count: errors.length })}
        </span>
        <span className="inline-flex items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-0.5 font-semibold text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/15 dark:text-amber-300">
          {t("TXT_WARNING_COUNT", { count: warnings.length })}
        </span>
      </div>
      <div className="dark-scrollbar min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
        {errorCode ? (
          <p role="alert" className="text-xs text-rose-600 dark:text-rose-400">
            {getErrorMessage(errorCode)}
          </p>
        ) : null}
        {!errorCode && (
          <ValidationIssueList
            issues={issues}
            onSelectTable={onSelectTable}
          />
        )}
      </div>
    </section>
  );
}
