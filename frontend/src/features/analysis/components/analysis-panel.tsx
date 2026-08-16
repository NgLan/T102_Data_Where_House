"use client";

import { useState } from "react";

import { cn } from "@/common/utils/cn";

import { countKeyDecisions, countWarnings } from "../model/sample-analysis";
import type { ModelAnalysis, TableAnalysis, WarningSeverity } from "../model/types";
import { AnalysisCard } from "./analysis-card";
import { Icon } from "./icon";

interface AnalysisPanelProps {
  analysis: ModelAnalysis;
  onClose: () => void;
}

type SectionKey = "grain" | "keys" | "warnings";

const WARNING_STYLES: Record<WarningSeverity, { badge: string; card: string; label: string }> = {
  critical: {
    badge: "bg-red-100 text-red-700",
    card: "border-red-100 bg-red-50/70",
    label: "Nghiêm trọng",
  },
  warning: {
    badge: "bg-amber-100 text-amber-700",
    card: "border-amber-100 bg-amber-50/70",
    label: "Cảnh báo",
  },
  info: {
    badge: "bg-blue-100 text-blue-700",
    card: "border-blue-100 bg-blue-50/70",
    label: "Lưu ý",
  },
};

/** Hiển thị chỉ số tổng quan của nội dung phân tích. */
function SummaryMetric({ value, label, icon }: { value: number; label: string; icon: "table" | "key" | "alert" }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-2.5">
      <div className="flex items-center gap-1.5 text-lg font-bold text-slate-800">
        <Icon name={icon} className="size-4 text-blue-600" />
        {value}
      </div>
      <p className="mt-0.5 text-[10px] font-medium text-slate-500">{label}</p>
    </div>
  );
}

/** Hiển thị danh sách cảnh báo và hướng xử lý do AI đề xuất. */
function WarningList({ table }: { table: TableAnalysis }) {
  if (table.warnings.length === 0) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50 p-3 text-emerald-800">
        <span className="grid size-7 shrink-0 place-items-center rounded-full bg-emerald-100"><Icon name="check" className="size-4" /></span>
        <div>
          <p className="text-xs font-bold">Không phát hiện vấn đề</p>
          <p className="mt-1 text-[11px] leading-5 text-emerald-700">Thiết kế hiện tại vượt qua các quy tắc kiểm tra anti-pattern.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {table.warnings.map((warning) => {
        const style = WARNING_STYLES[warning.severity];
        return (
          <article key={warning.code} className={cn("rounded-xl border p-3", style.card)}>
            <div className="flex flex-wrap items-center gap-2">
              <span className={cn("rounded-md px-2 py-1 text-[9px] font-extrabold uppercase", style.badge)}>{style.label}</span>
              <code className="text-[9px] font-bold text-slate-400">{warning.code}</code>
            </div>
            <h4 className="mt-2 text-xs font-bold text-slate-800">{warning.title}</h4>
            <p className="mt-1.5 text-[11px] leading-5 text-slate-600">{warning.message}</p>
            <div className="mt-3 rounded-lg border border-white/80 bg-white/80 p-2.5">
              <p className="text-[9px] font-extrabold tracking-wide text-slate-400 uppercase">AI đề xuất</p>
              <p className="mt-1 text-[11px] leading-5 text-slate-700">{warning.recommendation}</p>
            </div>
          </article>
        );
      })}
    </div>
  );
}

/** Hiển thị toàn bộ phần diễn giải AI và bộ lọc theo bảng. */
export function AnalysisPanel({ analysis, onClose }: AnalysisPanelProps) {
  const [selectedTableId, setSelectedTableId] = useState(analysis.tables[0]?.id ?? "");
  const [expanded, setExpanded] = useState<Record<SectionKey, boolean>>({
    grain: true,
    keys: true,
    warnings: true,
  });
  const selectedTable = analysis.tables.find((table) => table.id === selectedTableId) ?? analysis.tables[0];

  /** Đổi trạng thái mở rộng của một nhóm nội dung. */
  function toggleSection(section: SectionKey): void {
    setExpanded((current) => ({ ...current, [section]: !current[section] }));
  }

  if (!selectedTable) {
    return null;
  }

  return (
    <aside className="analysis-panel order-first flex min-h-0 w-full shrink-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_18px_45px_rgba(15,23,42,0.10)] min-[1380px]:order-none min-[1380px]:w-[590px]" aria-label="Nội dung phân tích của AI">
      <header className="border-b border-slate-200 px-5 pb-4 pt-5">
        <div className="flex items-start gap-3">
          <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-200">
            <Icon name="sparkles" className="size-5" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">Nội dung phân tích</h2>
              <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[9px] font-extrabold tracking-wide text-blue-700 uppercase">AI Insights</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Cập nhật {analysis.generatedAt} · Phiên bản {analysis.version}</p>
          </div>
          <div className="mr-1 text-right">
            <p className="text-lg font-black text-emerald-600">{analysis.qualityScore}</p>
            <p className="text-[9px] font-semibold text-slate-400">Điểm chất lượng</p>
          </div>
          <button type="button" aria-label="Đóng nội dung phân tích" onClick={onClose} className="grid size-8 shrink-0 place-items-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-2 focus-visible:outline-blue-600">
            <Icon name="close" className="size-[18px]" />
          </button>
        </div>
        <p className="mt-4 rounded-xl border border-blue-100 bg-blue-50/60 p-3 text-[11px] leading-5 text-slate-600">{analysis.summary}</p>
        <div className="mt-3 grid grid-cols-3 gap-2">
          <SummaryMetric value={analysis.tables.length} label="Grain đã xác định" icon="table" />
          <SummaryMetric value={countKeyDecisions(analysis)} label="Quyết định khóa" icon="key" />
          <SummaryMetric value={countWarnings(analysis)} label="Cảnh báo & lưu ý" icon="alert" />
        </div>
      </header>

      <div className="border-b border-slate-200 px-5 py-3">
        <label htmlFor="analysis-table" className="mb-1.5 block text-[10px] font-bold tracking-wide text-slate-500 uppercase">Phân tích theo bảng</label>
        <div className="relative">
          <select id="analysis-table" value={selectedTable.id} onChange={(event) => setSelectedTableId(event.target.value)} className="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 pr-9 text-xs font-semibold text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100">
            {analysis.tables.map((table) => (
              <option key={table.id} value={table.id}>{table.name} · {table.role} · {table.warnings.length} cảnh báo</option>
            ))}
          </select>
          <Icon name="chevron" className="pointer-events-none absolute right-3 top-2.5 size-4 rotate-90 text-slate-400" />
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto bg-slate-50/50 px-5 py-4">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">{selectedTable.name}</h3>
            <p className="mt-0.5 text-[10px] text-slate-500">Chi tiết quyết định thiết kế và rủi ro cần lưu ý</p>
          </div>
          <span className={cn("rounded-lg px-2.5 py-1 text-[9px] font-extrabold tracking-wide", selectedTable.role === "Fact" ? "bg-blue-100 text-blue-700" : "bg-violet-100 text-violet-700")}>{selectedTable.role}</span>
        </div>

        <div className="space-y-3">
          <AnalysisCard id="grain-content" title="Grain (Độ mịn dữ liệu)" eyebrow="Phạm vi một bản ghi" icon="layers" tone="emerald" expanded={expanded.grain} onToggle={() => toggleSection("grain")}>
            <p className="text-xs font-semibold leading-5 text-slate-800">{selectedTable.grain}</p>
            <div className="mt-3 border-l-2 border-emerald-300 pl-3">
              <p className="text-[9px] font-extrabold tracking-wide text-emerald-700 uppercase">Vì sao chọn Grain này?</p>
              <p className="mt-1 text-[11px] leading-5 text-slate-600">{selectedTable.grainRationale}</p>
            </div>
          </AnalysisCard>

          <AnalysisCard id="key-content" title={`${selectedTable.keyDecisions.length} quyết định khóa`} eyebrow="Primary key & Foreign key" icon="key" tone="blue" expanded={expanded.keys} onToggle={() => toggleSection("keys")}>
            <div className="space-y-3">
              {selectedTable.keyDecisions.map((decision) => (
                <article key={decision.column} className="rounded-xl bg-slate-50 p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <code className="rounded-md bg-slate-800 px-2 py-1 text-[10px] font-bold text-white">{decision.column}</code>
                    <span className="text-[9px] font-bold text-blue-600 uppercase">{decision.kind}</span>
                    {decision.reference && <span className="text-[9px] text-slate-400">→ {decision.reference}</span>}
                  </div>
                  <p className="mt-2 text-[11px] leading-5 text-slate-600">{decision.rationale}</p>
                </article>
              ))}
            </div>
          </AnalysisCard>

          <AnalysisCard id="warning-content" title={selectedTable.warnings.length ? `${selectedTable.warnings.length} cảnh báo cần xem` : "Không có cảnh báo"} eyebrow="Kiểm tra Anti-pattern" icon="alert" tone="amber" expanded={expanded.warnings} onToggle={() => toggleSection("warnings")}>
            <WarningList table={selectedTable} />
          </AnalysisCard>
        </div>
      </div>
    </aside>
  );
}
