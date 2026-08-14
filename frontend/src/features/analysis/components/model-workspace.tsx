"use client";

import { useState } from "react";

import { cn } from "@/common/utils/cn";

import { countWarnings, SAMPLE_ANALYSIS } from "../model/sample-analysis";
import { AnalysisPanel } from "./analysis-panel";
import { DataModelCanvas } from "./data-model-canvas";
import { DdlViewer } from "./ddl-viewer";
import { Icon, type IconName } from "./icon";

interface NavigationItem {
  label: string;
  icon: IconName;
  active?: boolean;
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  { label: "Tổng quan", icon: "grid" },
  { label: "Nguồn dữ liệu", icon: "database" },
  { label: "Yêu cầu nghiệp vụ", icon: "layers" },
  { label: "Mô hình dữ liệu", icon: "network", active: true },
  { label: "Lịch sử phiên", icon: "code" },
];

/** Hiển thị mục điều hướng chính của workspace. */
function NavigationLink({ item }: { item: NavigationItem }) {
  return (
    <button type="button" className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-semibold transition", item.active ? "bg-blue-50 text-blue-700" : "text-slate-500 hover:bg-slate-50 hover:text-slate-800")}>
      <Icon name={item.icon} className="size-[18px]" />
      {item.label}
      {item.active && <span className="ml-auto size-1.5 rounded-full bg-blue-600" />}
    </button>
  );
}

/** Hiển thị toàn bộ workspace mô hình và điều khiển đóng/mở phân tích AI. */
export function ModelWorkspace() {
  const [analysisOpen, setAnalysisOpen] = useState(true);
  const [ddlOpen, setDdlOpen] = useState(false);
  const warningCount = countWarnings(SAMPLE_ANALYSIS);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="sticky top-0 z-30 flex h-16 items-center border-b border-slate-200 bg-white px-4 lg:px-6">
        <button type="button" className="mr-3 grid size-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 md:hidden" aria-label="Mở menu"><Icon name="menu" /></button>
        <div className="flex items-center gap-3">
          <span className="relative grid size-9 place-items-center overflow-hidden rounded-xl bg-blue-600 text-white shadow-md shadow-blue-200">
            <span className="absolute -right-2 -top-2 size-5 rounded-full border-4 border-blue-400" />
            <Icon name="database" className="size-[18px]" />
          </span>
          <div>
            <p className="text-sm font-extrabold tracking-tight text-slate-900">DataCraft AI</p>
            <p className="text-[9px] font-semibold tracking-[0.16em] text-slate-400 uppercase">Modeling workspace</p>
          </div>
        </div>
        <div className="mx-6 hidden h-6 w-px bg-slate-200 md:block" />
        <nav aria-label="Đường dẫn" className="hidden items-center gap-2 text-[11px] text-slate-400 md:flex">
          <span>Dự án</span><Icon name="chevron" className="size-3" />
          <span>Ride Analytics</span><Icon name="chevron" className="size-3" />
          <span className="font-semibold text-slate-700">Mô hình dữ liệu</span>
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <span className="hidden items-center gap-1.5 text-[10px] font-semibold text-emerald-700 sm:flex"><span className="size-2 rounded-full bg-emerald-500 shadow-[0_0_0_3px_#d1fae5]" />Đã lưu</span>
          <button type="button" className="grid size-9 place-items-center rounded-full bg-gradient-to-br from-slate-700 to-slate-900 text-xs font-bold text-white" aria-label="Tài khoản của Minh Anh">MA</button>
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-4rem)]">
        <aside className="hidden w-60 shrink-0 border-r border-slate-200 bg-white p-4 md:flex md:flex-col">
          <div className="mb-5 rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-[9px] font-bold tracking-wider text-slate-400 uppercase">Dự án hiện tại</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-lg bg-violet-100 text-violet-700"><Icon name="layers" className="size-4" /></span>
              <div className="min-w-0"><p className="truncate text-xs font-bold text-slate-800">Ride Analytics</p><p className="text-[9px] text-slate-400">BigQuery · Production</p></div>
            </div>
          </div>
          <p className="mb-2 px-3 text-[9px] font-bold tracking-[0.14em] text-slate-400 uppercase">Workspace</p>
          <nav className="space-y-1" aria-label="Điều hướng workspace">
            {NAVIGATION_ITEMS.map((item) => <NavigationLink key={item.label} item={item} />)}
          </nav>
          <div className="mt-auto rounded-2xl bg-slate-900 p-4 text-white">
            <div className="flex items-center gap-2 text-xs font-bold"><Icon name="brain" className="size-4 text-blue-300" />AI Copilot</div>
            <p className="mt-2 text-[10px] leading-4 text-slate-400">Mô hình đã được kiểm tra theo 18 quy tắc Kimball.</p>
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-700"><div className="h-full w-[92%] rounded-full bg-blue-500" /></div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col p-4 lg:p-5">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
            <div>
              <div className="flex items-center gap-2"><h1 className="text-xl font-extrabold tracking-tight text-slate-900 lg:text-2xl">Mô hình dữ liệu</h1><span className="rounded-md bg-slate-200 px-2 py-1 text-[9px] font-bold text-slate-600">v12</span></div>
              <p className="mt-1 text-[11px] text-slate-500">Thiết kế, kiểm tra và diễn giải cấu trúc Data Warehouse cùng AI.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" onClick={() => setDdlOpen(true)} className="flex h-9 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-[11px] font-bold text-slate-600 shadow-sm transition hover:border-blue-300 hover:text-blue-700"><Icon name="code" className="size-4" />Xem mã DDL</button>
              <button type="button" className="flex h-9 items-center gap-2 rounded-xl bg-blue-600 px-3 text-[11px] font-bold text-white shadow-md shadow-blue-200 transition hover:bg-blue-700"><Icon name="save" className="size-4" />Lưu thay đổi</button>
            </div>
          </div>

          <div className="mb-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-2 py-2 shadow-sm">
            <div className="flex items-center gap-1" role="tablist" aria-label="Chế độ xem mô hình">
              <button type="button" role="tab" aria-selected="true" className="flex h-8 items-center gap-2 rounded-lg bg-slate-100 px-3 text-[10px] font-bold text-slate-800"><Icon name="network" className="size-4 text-blue-600" />Sơ đồ ERD</button>
              <button type="button" role="tab" aria-selected="false" className="flex h-8 items-center gap-2 rounded-lg px-3 text-[10px] font-semibold text-slate-500 hover:bg-slate-50"><Icon name="code" className="size-4" />Mã DBML</button>
              <button type="button" role="tab" aria-selected="false" className="hidden h-8 items-center gap-2 rounded-lg px-3 text-[10px] font-semibold text-slate-500 hover:bg-slate-50 sm:flex"><Icon name="table" className="size-4" />Danh sách bảng</button>
            </div>
            <button type="button" aria-expanded={analysisOpen} aria-controls="ai-analysis-panel" onClick={() => setAnalysisOpen((open) => !open)} className={cn("flex h-8 items-center gap-2 rounded-lg border px-3 text-[10px] font-bold transition focus-visible:outline-2 focus-visible:outline-blue-600", analysisOpen ? "border-blue-200 bg-blue-50 text-blue-700" : "border-slate-200 bg-white text-slate-600 hover:border-blue-200 hover:text-blue-700")}>
              <Icon name="sparkles" className="size-4" />{analysisOpen ? "Đang xem phân tích" : "Xem nội dung phân tích"}<span className="grid size-5 place-items-center rounded-full bg-amber-100 text-[9px] text-amber-700">{warningCount}</span>
            </button>
          </div>

          <div id="ai-analysis-panel" className="flex min-h-0 flex-1 flex-col gap-4 min-[1380px]:flex-row">
            <DataModelCanvas />
            {analysisOpen && <AnalysisPanel analysis={SAMPLE_ANALYSIS} onClose={() => setAnalysisOpen(false)} />}
          </div>
        </main>
      </div>
      <DdlViewer open={ddlOpen} onClose={() => setDdlOpen(false)} />
    </div>
  );
}
