"use client";

import { useEffect, useState } from "react";

import { cn } from "@/common/utils/cn";

import { useDdlDocument } from "../hooks/use-ddl-document";
import type { DdlDialect } from "../model/ddl-types";
import { CURRENT_MODEL } from "../model/sample-data-model";
import { Icon } from "./icon";

interface DdlViewerProps {
  open: boolean;
  onClose: () => void;
}

const DIALECT_LABELS: Record<DdlDialect, string> = {
  postgresql: "PostgreSQL",
  bigquery: "Google BigQuery",
  snowflake: "Snowflake",
};

/** Hiển thị trạng thái đang sinh mã DDL. */
function DdlLoading() {
  return (
    <div className="space-y-3 p-6" aria-label="Đang sinh mã DDL">
      {[92, 75, 84, 60, 88, 70].map((width, index) => (
        <div key={index} className="flex gap-4">
          <span className="h-3 w-5 animate-pulse rounded bg-slate-700" />
          <span className="h-3 animate-pulse rounded bg-slate-700" style={{ width: `${width}%` }} />
        </div>
      ))}
    </div>
  );
}

/** Hiển thị lỗi tải DDL cùng hành động thử lại. */
function DdlError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="grid min-h-80 place-items-center p-8 text-center">
      <div className="max-w-sm">
        <span className="mx-auto grid size-12 place-items-center rounded-2xl bg-red-100 text-red-600"><Icon name="alert" /></span>
        <h3 className="mt-4 text-sm font-bold text-white">Chưa thể sinh mã DDL</h3>
        <p className="mt-2 text-xs leading-5 text-slate-400">{message}</p>
        <button type="button" onClick={onRetry} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-bold text-white hover:bg-blue-500"><Icon name="refresh" className="size-4" />Thử lại</button>
      </div>
    </div>
  );
}

/** Hiển thị mã DDL kèm số dòng để người dùng đọc và đối chiếu. */
function DdlCode({ content }: { content: string }) {
  return (
    <pre className="min-w-max py-5 font-mono text-[12px] leading-6 text-slate-200">
      {content.split("\n").map((line, index) => (
        <span key={`${index}-${line}`} className="block pr-8 hover:bg-slate-800/80">
          <span className="mr-5 inline-block w-10 select-none border-r border-slate-700 pr-3 text-right text-slate-600">{index + 1}</span>
          <code>{line || " "}</code>
        </span>
      ))}
    </pre>
  );
}

/** Hiển thị dialog xem DDL sinh từ revision mô hình hiện tại. */
export function DdlViewer({ open, onClose }: DdlViewerProps) {
  const [dialect, setDialect] = useState<DdlDialect>("postgresql");
  const [copied, setCopied] = useState(false);
  const modelRequest = CURRENT_MODEL;
  const { document: ddlDocument, error, loading, retry } = useDdlDocument(open, dialect, modelRequest);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = documentBodyOverflow();
    document.body.style.overflow = "hidden";
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [onClose, open]);

  /** Sao chép toàn bộ DDL đang hiển thị vào clipboard. */
  async function copyDdl(): Promise<void> {
    if (!ddlDocument) return;
    await navigator.clipboard.writeText(ddlDocument.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/55 p-3 backdrop-blur-sm sm:p-6" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section role="dialog" aria-modal="true" aria-labelledby="ddl-dialog-title" className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <header className="flex flex-wrap items-start gap-3 border-b border-slate-200 px-5 py-4">
          <span className="grid size-10 place-items-center rounded-xl bg-slate-900 text-blue-300"><Icon name="code" /></span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2"><h2 id="ddl-dialog-title" className="text-base font-extrabold text-slate-900">Mã DDL của mô hình hiện tại</h2><span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[9px] font-bold text-emerald-700">READ ONLY</span></div>
            <p className="mt-1 text-[11px] text-slate-500">{CURRENT_MODEL.model_name} · Revision {CURRENT_MODEL.revision}</p>
          </div>
          <button type="button" aria-label="Đóng cửa sổ DDL" onClick={onClose} className="grid size-8 place-items-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700"><Icon name="close" className="size-[18px]" /></button>
        </header>

        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-slate-50 px-5 py-3">
          <div className="flex items-center gap-2">
            <label htmlFor="ddl-dialect" className="text-[10px] font-bold text-slate-500">Hệ quản trị</label>
            <select id="ddl-dialect" value={dialect} onChange={(event) => setDialect(event.target.value as DdlDialect)} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-[11px] font-bold text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100">
              {Object.entries(DIALECT_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
          <button type="button" disabled={!ddlDocument || loading} onClick={copyDdl} className={cn("inline-flex h-9 items-center gap-2 rounded-lg px-3 text-[11px] font-bold transition", copied ? "bg-emerald-100 text-emerald-700" : "border border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-blue-700", (!ddlDocument || loading) && "cursor-not-allowed opacity-50")}>
            <Icon name={copied ? "check" : "copy"} className="size-4" />{copied ? "Đã sao chép" : "Sao chép DDL"}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-auto bg-[#0b1120]">
          {loading && <DdlLoading />}
          {!loading && error && <DdlError message={error} onRetry={retry} />}
          {!loading && ddlDocument && <DdlCode content={ddlDocument.content} />}
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 px-5 py-3 text-[10px] text-slate-500">
          <span>{ddlDocument ? `${ddlDocument.table_count} bảng · ${DIALECT_LABELS[ddlDocument.dialect]}` : "DDL được sinh trực tiếp từ DBML hiện tại"}</span>
          <span className="flex items-center gap-1.5"><Icon name="check" className="size-3.5 text-emerald-600" />Không thực thi lên cơ sở dữ liệu</span>
        </footer>
      </section>
    </div>
  );
}

/** Đọc trạng thái overflow hiện tại trước khi khóa cuộn trang. */
function documentBodyOverflow(): string {
  return document.body.style.overflow;
}
