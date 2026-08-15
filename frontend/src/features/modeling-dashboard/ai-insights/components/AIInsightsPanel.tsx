"use client";

import { Bot, Filter, Sparkles, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { AIInsight } from "../types/ai-insight-types";
import { Button } from "@/common/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { AIInsightCard } from "./AIInsightCard";

interface AIInsightsPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  selectedFilter: string;
  onFilterChange: (value: string) => void;
  insights: AIInsight[];
  tableNames: string[];
  totalCount: number;
}

/** Hiển thị drawer AI insights và bộ lọc theo bảng.
 * @param props Widget state, insight data và callback tương tác.
 * @returns Floating drawer sử dụng shadcn controls.
 */
export function AIInsightsPanel(props: AIInsightsPanelProps) {
  const { t } = useTranslation("modeling-dashboard");
  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-50 flex flex-col items-end">
      <section
        className={`mb-4 flex max-h-[500px] w-92 max-w-[calc(100vw-32px)] origin-bottom-right flex-col overflow-hidden rounded-2xl border border-slate-200/90 bg-white/95 shadow-2xl backdrop-blur-md transition-all duration-300 ${props.isOpen ? "pointer-events-auto translate-y-0 scale-100 opacity-100" : "pointer-events-none translate-y-4 scale-90 opacity-0"}`}
      >
        <header className="flex items-center justify-between bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-4 py-3.5 text-white">
          <div className="flex items-center gap-2 text-xs font-bold">
            <span className="flex size-7 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-500/20 text-sky-400">
              <Bot className="size-4" />
            </span>
            <span>{t("TXT_AI_INSIGHTS")}</span>
            <span className="rounded-full border border-amber-500/30 bg-amber-500/20 px-2 py-0.5 text-[10px] text-amber-300">
              {t("TXT_ISSUE_COUNT", { count: props.totalCount })}
            </span>
          </div>
          <Button
            type="button"
            size="icon-xs"
            variant="ghost"
            onClick={props.onToggle}
            aria-label={t("BTN_TOGGLE_INSIGHTS")}
          >
            <X />
          </Button>
        </header>
        <div className="flex flex-1 flex-col gap-3 overflow-hidden p-3.5">
          <div className="flex items-center gap-2">
            <Filter className="size-3.5 shrink-0 text-slate-400" />
            <NativeSelect
              className="w-full"
              value={props.selectedFilter}
              onChange={(event) => props.onFilterChange(event.target.value)}
            >
              <NativeSelectOption value="ALL">
                {t("TXT_ALL_TABLES", { count: props.totalCount })}
              </NativeSelectOption>
              {props.tableNames.map((name) => (
                <NativeSelectOption key={name} value={name}>
                  {name}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </div>
          <div className="flex max-h-[340px] flex-col gap-2 overflow-y-auto pr-1">
            {props.insights.length > 0 ? (
              props.insights.map((item) => (
                <AIInsightCard key={item.id} item={item} />
              ))
            ) : (
              <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed p-4 text-center text-xs text-slate-500">
                <Bot className="size-8 text-slate-300" />
                <p>{t("TXT_EMPTY_INSIGHTS")}</p>
              </div>
            )}
          </div>
        </div>
      </section>
      <Button
        type="button"
        size="icon-lg"
        onClick={props.onToggle}
        title={t("BTN_TOGGLE_INSIGHTS")}
        className="pointer-events-auto group relative size-14 cursor-pointer rounded-full bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 shadow-xl shadow-blue-600/30 hover:scale-105 hover:from-blue-500 hover:to-violet-500"
      >
        <Sparkles className="size-6 transition-transform group-hover:rotate-12" />
        {props.totalCount > 0 && (
          <span className="absolute -right-1 -top-1 flex size-6 items-center justify-center rounded-full border-2 border-white bg-rose-500 text-[11px] font-bold text-white">
            {props.totalCount}
          </span>
        )}
      </Button>
    </div>
  );
}
