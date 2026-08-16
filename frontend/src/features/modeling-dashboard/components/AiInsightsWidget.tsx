/**
 * Presentation Component: Floating AI Insights Widget - Trợ lý phân tích cảnh báo góc màn hình
 * Glassmorphic Drawer với filter bảng & badge số lượng cảnh báo nổi
 */

import React from 'react';
import { InsightItemDto } from '@/api/model/erd.dto';
import { InsightCard } from './InsightCard';
import { Sparkles, AlertTriangle, X, Filter, Bot } from 'lucide-react';

export interface AiInsightsWidgetProps {
  isOpen: boolean;
  onToggle: () => void;
  selectedFilter: string;
  onFilterChange: (value: string) => void;
  insights: InsightItemDto[];
  totalCount: number;
}

export const AiInsightsWidget: React.FC<AiInsightsWidgetProps> = ({
  isOpen,
  onToggle,
  selectedFilter,
  onFilterChange,
  insights,
  totalCount,
}) => {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Floating Insights Drawer Card */}
      <div
        className={`mb-4 w-92 max-w-[calc(100vw-32px)] max-h-[500px] bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 transform-gpu origin-bottom-right ${
          isOpen
            ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto'
            : 'opacity-0 scale-90 translate-y-4 pointer-events-none'
        }`}
      >
        {/* Header */}
        <div className="px-4 py-3.5 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex justify-between items-center shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold tracking-wide">
            <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <span>AI INSIGHTS & GRAIN AUDIT</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {totalCount} Issue{totalCount > 1 ? 's' : ''}
            </span>
          </div>

          <button
            onClick={onToggle}
            className="w-6 h-6 rounded-full bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center text-xs transition cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-3.5 flex flex-col gap-3 overflow-hidden flex-1">
          {/* Table Filter Dropdown */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <select
              className="flex-1 px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50/80 font-semibold text-slate-700 outline-none focus:border-blue-500 transition cursor-pointer"
              value={selectedFilter}
              onChange={(e) => onFilterChange(e.target.value)}
            >
              <option value="ALL">-- Tất cả các bảng ({totalCount} cảnh báo) --</option>
              <option value="Fact_Rides">Fact_Rides (2 cảnh báo)</option>
              <option value="Dim_Driver">Dim_Driver (1 cảnh báo)</option>
              <option value="Dim_Customer">Dim_Customer (1 cảnh báo)</option>
              <option value="Dim_Promo">Dim_Promo (1 cảnh báo)</option>
            </select>
          </div>

          {/* Insights Items Container */}
          <div className="flex flex-col gap-2 overflow-y-auto pr-1 dark-scrollbar max-h-[340px]">
            {insights.map((item) => (
              <InsightCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      </div>

      {/* Trigger Button - Floating Action Button (FAB) */}
      <button
        onClick={onToggle}
        className="relative group w-14 h-14 rounded-full text-white cursor-pointer flex items-center justify-center transition-all duration-300 shadow-xl shadow-blue-600/30 hover:scale-105 active:scale-95 glow-btn-primary border border-white/20"
        title="AI Insights & Cảnh báo tự động"
      >
        <Sparkles className="w-6 h-6 text-white group-hover:rotate-12 transition-transform duration-300" />

        {totalCount > 0 && (
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-rose-500 text-white text-[11px] font-bold rounded-full border-2 border-white flex items-center justify-center shadow-md animate-bounce">
            {totalCount}
          </span>
        )}
      </button>
    </div>
  );
};

