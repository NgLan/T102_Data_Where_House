"use client";

import { Loader2, ShieldAlert, ShieldCheck } from "lucide-react";
import { useTranslation } from "react-i18next";

interface ValidationTriggerButtonProps {
  isValidating: boolean;
  hasErrors: boolean;
  hasWarnings: boolean;
  totalIssues: number;
  isDragging: boolean;
  dragHandlers: {
    onPointerDown: (e: React.PointerEvent) => void;
    onPointerMove: (e: React.PointerEvent) => void;
    onPointerUp: (e: React.PointerEvent) => void;
  };
}

export function ValidationTriggerButton({
  isValidating,
  hasErrors,
  hasWarnings,
  totalIssues,
  isDragging,
  dragHandlers,
}: ValidationTriggerButtonProps) {
  const { t } = useTranslation("modeling-workspace");

  return (
    <div
      {...dragHandlers}
      className="pointer-events-auto relative cursor-grab active:cursor-grabbing select-none touch-none rounded-full"
    >
      <button
        type="button"
        aria-label={t("TXT_VALIDATION_ENGINE")}
        className={`flex size-13 items-center justify-center rounded-full border-2 transition-all ${
          hasErrors
            ? "border-rose-500 bg-white text-rose-600 ring-4 ring-rose-500/20 shadow-lg shadow-rose-950/20 dark:border-rose-500/80 dark:bg-slate-900 dark:text-rose-400 dark:shadow-rose-950/40"
            : hasWarnings
              ? "border-amber-500 bg-white text-amber-600 ring-4 ring-amber-500/20 shadow-lg shadow-amber-950/20 dark:border-amber-500/80 dark:bg-slate-900 dark:text-amber-400 dark:shadow-amber-950/40"
              : "border-sky-500 bg-white text-sky-600 ring-4 ring-sky-500/20 shadow-lg shadow-sky-950/20 dark:border-sky-500/80 dark:bg-slate-900 dark:text-sky-400 dark:shadow-sky-950/40"
        } ${
          isDragging
            ? "scale-110 opacity-90 shadow-2xl cursor-grabbing"
            : "hover:scale-105 active:scale-95"
        }`}
      >
        {isValidating ? (
          <Loader2 className="size-5.5 animate-spin" />
        ) : hasErrors ? (
          <ShieldAlert className="size-5.5" />
        ) : (
          <ShieldCheck className="size-5.5" />
        )}
        {totalIssues > 0 && (
          <span
            className={`absolute -right-1 -top-1 flex size-5.5 items-center justify-center rounded-full text-[11px] font-bold ring-2 ring-white dark:ring-slate-950 ${
              hasErrors
                ? "bg-rose-600 text-white dark:bg-rose-500"
                : "bg-amber-500 text-white dark:bg-amber-400 dark:text-slate-950"
            }`}
          >
            {totalIssues}
          </span>
        )}
      </button>
    </div>
  );
}
