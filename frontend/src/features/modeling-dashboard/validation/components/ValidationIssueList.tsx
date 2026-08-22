"use client";

import { AlertTriangle, CheckCircle2, Table2, XCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DataModelValidationIssueResponse } from "@/api";

export function ValidationIssueList(props: {
  issues: DataModelValidationIssueResponse[];
  onSelectTable: (tableName: string) => void;
}) {
  if (props.issues.length === 0) return <ValidationEmpty />;
  return (
    <div className="space-y-2.5">
      {props.issues.map((issue, index) => (
        <ValidationIssue
          key={`${issue.code}-${issue.table_name}-${issue.column_name}-${index}`}
          issue={issue}
          onSelectTable={props.onSelectTable}
        />
      ))}
    </div>
  );
}

function ValidationIssue(props: {
  issue: DataModelValidationIssueResponse;
  onSelectTable: (tableName: string) => void;
}) {
  const { issue } = props;
  const isError = issue.severity === "ERROR";
  const Icon = isError ? XCircle : AlertTriangle;

  return (
    <article
      className={`rounded-xl border p-3.5 shadow-xs transition-colors ${
        isError
          ? "border-rose-200 bg-rose-50/70 hover:border-rose-300 text-slate-900 dark:border-rose-500/30 dark:bg-rose-950/25 dark:hover:border-rose-500/50 dark:text-slate-100"
          : "border-amber-200 bg-amber-50/70 hover:border-amber-300 text-slate-900 dark:border-amber-500/30 dark:bg-amber-950/20 dark:hover:border-amber-500/50 dark:text-slate-100"
      }`}
    >
      <div className="flex items-start gap-2.5">
        <Icon
          className={`size-4 shrink-0 mt-0.5 ${
            isError
              ? "text-rose-600 dark:text-rose-400"
              : "text-amber-600 dark:text-amber-400"
          }`}
        />
        <div className="min-w-0 flex-1">
          <strong
            className={`block text-xs font-semibold ${
              isError
                ? "text-rose-900 dark:text-rose-200"
                : "text-amber-900 dark:text-amber-200"
            }`}
          >
            {issue.title}
          </strong>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
            {issue.description}
          </p>
          {issue.table_name && (
            <button
              type="button"
              onClick={() => props.onSelectTable(issue.table_name!)}
              className="mt-2 inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-300 bg-slate-100/90 px-2 py-0.5 font-mono text-[11px] font-medium text-sky-700 transition-colors hover:border-sky-400 hover:bg-sky-50 hover:text-sky-800 dark:border-slate-700/80 dark:bg-slate-800/90 dark:text-sky-300 dark:hover:border-sky-500/50 dark:hover:bg-slate-700/90 dark:hover:text-sky-200"
            >
              <Table2 className="size-3 text-sky-600 dark:text-sky-400" />
              <span>
                {issue.table_name}
                {issue.column_name ? `.${issue.column_name}` : ""}
              </span>
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

function ValidationEmpty() {
  const { t } = useTranslation("modeling-workspace");
  return (
    <div className="flex flex-col items-center justify-center gap-2 p-6 text-center text-xs text-slate-600 dark:text-slate-300">
      <CheckCircle2 className="size-7 text-emerald-600 dark:text-emerald-400" />
      <span className="font-medium text-slate-800 dark:text-slate-200">
        {t("TXT_VALIDATION_EMPTY")}
      </span>
    </div>
  );
}
