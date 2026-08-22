"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { AlertTriangle, KeyRound, XCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/common/components/ui/tooltip";
import type { ERDTableNode as ERDTableNodeType } from "../types/erd-canvas-types";
import { createColumnHandle } from "../utils/erd-graph-mapper";

/** Hiển thị một bảng DBML có handle theo từng cột với độ tương phản cao ở cả Light & Dark modes. */
export function ERDTableNode({ data, selected }: NodeProps<ERDTableNodeType>) {
  const { t } = useTranslation("model-inspector");
  const { table, foreignKeyColumnIds, validationIssues = [] } = data;
  const hasError = validationIssues.some((item) => item.severity === "ERROR");
  const headerTone = hasError
    ? "border-b border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-600/60 dark:bg-rose-950/60 dark:text-rose-200"
    : validationIssues.length > 0
      ? "border-b border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-600/60 dark:bg-amber-950/60 dark:text-amber-200"
      : "border-b border-slate-200 bg-slate-100 text-slate-900 dark:border-slate-700/80 dark:bg-slate-800 dark:text-slate-100";

  return (
    <article
      className={`w-[270px] overflow-hidden rounded-xl border bg-white shadow-md transition-all dark:bg-slate-900/95 dark:shadow-xl dark:shadow-black/50 ${
        selected
          ? "border-sky-500 ring-2 ring-sky-500/30 shadow-lg shadow-sky-500/10 dark:border-sky-400 dark:ring-sky-400/30"
          : "border-slate-300 dark:border-slate-700/80"
      }`}
    >
      <header
        className={`flex items-start gap-2 px-3.5 py-2.5 text-xs font-bold ${headerTone}`}
      >
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm">{table.name}</span>
          {table.schemaName && (
            <span className="text-[10px] font-normal text-slate-500 dark:text-slate-400">
              {table.schemaName}
            </span>
          )}
        </span>
        {validationIssues.length > 0 && (
          <TableIssueTooltip issues={validationIssues} hasError={hasError} />
        )}
      </header>
      <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
        {table.columns.map((column) => {
          const isPK = column.isPrimaryKey;
          const isFK = foreignKeyColumnIds?.includes(column.id);
          return (
            <div
              key={column.id}
              className="relative flex h-8 items-center justify-between gap-2 px-3 text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40"
            >
              <Handle
                id={createColumnHandle(table.id, column.id, "target")}
                type="target"
                position={Position.Left}
                className="!size-2.5 !border-2 !border-white !bg-slate-400 shadow-xs dark:!border-slate-900 dark:!bg-slate-500"
              />
              <span className="flex min-w-0 items-center gap-1.5 truncate font-medium text-slate-800 dark:text-slate-200">
                {isPK ? (
                  <KeyRound
                    className="size-3.5 shrink-0 text-amber-500 dark:text-amber-400"
                    aria-label={t("PRIMARY_KEY_LABEL")}
                  />
                ) : isFK ? (
                  <KeyRound
                    className="size-3.5 shrink-0 text-sky-600 dark:text-sky-400"
                    aria-label={t("FOREIGN_KEY_LABEL")}
                  />
                ) : null}
                <span className="truncate">{column.name}</span>
              </span>
              <span className="shrink-0 font-mono text-[11px] font-medium text-slate-500 dark:text-sky-300/85">
                {column.dataType}
              </span>
              <Handle
                id={createColumnHandle(table.id, column.id, "source")}
                type="source"
                position={Position.Right}
                className="!size-2.5 !border-2 !border-white !bg-sky-500 shadow-xs dark:!border-slate-900 dark:!bg-sky-400"
              />
            </div>
          );
        })}
      </div>
    </article>
  );
}

function TableIssueTooltip({
  issues,
  hasError,
}: {
  issues: ERDTableNodeType["data"]["validationIssues"];
  hasError: boolean;
}) {
  const Icon = hasError ? XCircle : AlertTriangle;
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            className="shrink-0 cursor-pointer rounded-sm hover:opacity-80"
            aria-label={issues?.map((item) => item.title).join(", ")}
          >
            <Icon
              className={`size-4 ${
                hasError
                  ? "text-rose-600 dark:text-rose-400"
                  : "text-amber-600 dark:text-amber-400"
              }`}
            />
          </button>
        </TooltipTrigger>
        <TooltipContent side="right">
          <ul className="max-w-xs space-y-1">
            {issues?.map((item, index) => (
              <li key={`${item.code}-${index}`}>
                {item.title}: {item.description}
              </li>
            ))}
          </ul>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
