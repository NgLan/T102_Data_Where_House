"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { KeyRound } from "lucide-react";
import type { ERDTableNode as ERDTableNodeType } from "../types/erd-canvas-types";
import { createColumnHandle } from "../utils/erd-graph-mapper";

/** Hiển thị một bảng DBML có handle theo từng cột.
 * @param props Node props do React Flow cung cấp.
 * @returns Card bảng tương tác được trên ERD canvas.
 */
export function ERDTableNode({ data, selected }: NodeProps<ERDTableNodeType>) {
  const { table, foreignKeyColumnIds } = data;
  return (
    <article
      className={`w-[260px] overflow-hidden rounded-lg border bg-white shadow-sm ${selected ? "border-blue-500 ring-2 ring-blue-100" : "border-slate-300"}`}
    >
      <header className="border-b border-slate-200 bg-slate-900 px-3 py-2 text-sm font-semibold text-white">
        <span className="block truncate">{table.name}</span>
        {table.schemaName && (
          <span className="text-[10px] font-normal text-slate-400">
            {table.schemaName}
          </span>
        )}
      </header>
      <div className="divide-y divide-slate-100">
        {table.columns.map((column) => {
          const isPK = column.isPrimaryKey;
          const isFK = foreignKeyColumnIds?.includes(column.id);
          return (
            <div
              key={column.id}
              className="relative flex h-8 items-center justify-between gap-2 px-3 text-xs"
            >
              <Handle
                id={createColumnHandle(table.id, column.id, "target")}
                type="target"
                position={Position.Left}
                className="!size-2 !border-white !bg-slate-500"
              />
              <span className="flex min-w-0 items-center gap-1.5 truncate font-medium text-slate-700">
                {isPK ? (
                  <KeyRound
                    className="size-3 text-amber-500 shrink-0"
                    aria-label="Primary Key"
                  />
                ) : isFK ? (
                  <KeyRound
                    className="size-3 text-blue-500 shrink-0"
                    aria-label="Foreign Key"
                  />
                ) : null}
                <span className="truncate">{column.name}</span>
              </span>
              <span className="shrink-0 font-mono text-[10px] text-slate-400">
                {column.dataType}
              </span>
              <Handle
                id={createColumnHandle(table.id, column.id, "source")}
                type="source"
                position={Position.Right}
                className="!size-2 !border-white !bg-blue-500"
              />
            </div>
          );
        })}
      </div>
    </article>
  );
}
