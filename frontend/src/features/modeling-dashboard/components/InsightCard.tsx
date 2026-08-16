/**
 * Presentation Component: Insight Card item trong danh sách cảnh báo AI
 * Thẻ hiển thị cảnh báo với severity icons & table badge
 */

import React from 'react';
import { InsightItemDto } from '@/api/model/erd.dto';
import { AlertCircle, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export interface InsightCardProps {
  item: InsightItemDto;
}

export const InsightCard: React.FC<InsightCardProps> = ({ item }) => {
  const severityMap: Record<string, { cls: string; icon: React.ReactNode; badgeCls: string }> = {
    error: {
      cls: 'bg-rose-50/80 border-l-rose-500 text-rose-950 border-rose-200/60',
      icon: <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />,
      badgeCls: 'bg-rose-100 text-rose-700 border-rose-200',
    },
    warn: {
      cls: 'bg-amber-50/80 border-l-amber-500 text-amber-950 border-amber-200/60',
      icon: <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />,
      badgeCls: 'bg-amber-100 text-amber-800 border-amber-200',
    },
    info: {
      cls: 'bg-blue-50/80 border-l-blue-500 text-blue-950 border-blue-200/60',
      icon: <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />,
      badgeCls: 'bg-blue-100 text-blue-700 border-blue-200',
    },
  };

  const { cls, icon, badgeCls } = severityMap[item.severity] ?? severityMap['info'];

  return (
    <div
      className={`p-3 rounded-xl text-xs border border-l-4 transition-all shadow-2xs hover:shadow-xs flex items-start justify-between gap-2 leading-relaxed ${cls}`}
    >
      <div className="flex items-start gap-2 flex-1">
        {icon}
        <div>
          <b className="font-bold text-slate-900 block mb-0.5">{item.title}</b>
          <span className="text-[11.5px] text-slate-700">{item.description}</span>
        </div>
      </div>

      <span
        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border whitespace-nowrap uppercase font-mono ${badgeCls}`}
      >
        {item.table_name}
      </span>
    </div>
  );
};

