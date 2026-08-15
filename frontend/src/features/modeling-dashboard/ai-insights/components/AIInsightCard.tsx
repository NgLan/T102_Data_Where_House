import type { ReactNode } from "react";
import { AlertCircle, AlertTriangle, Info } from "lucide-react";
import type { AIInsight } from "../types/ai-insight-types";

interface AIInsightCardProps {
  item: AIInsight;
}

const APPEARANCE: Record<
  AIInsight["severity"],
  { className: string; icon: ReactNode }
> = {
  error: {
    className: "border-rose-200 border-l-rose-500 bg-rose-50 text-rose-950",
    icon: <AlertCircle className="size-4 text-rose-600" />,
  },
  warn: {
    className: "border-amber-200 border-l-amber-500 bg-amber-50 text-amber-950",
    icon: <AlertTriangle className="size-4 text-amber-600" />,
  },
  info: {
    className: "border-blue-200 border-l-blue-500 bg-blue-50 text-blue-950",
    icon: <Info className="size-4 text-blue-600" />,
  },
};

/** Hiển thị một cảnh báo AI Insights.
 * @param props Insight view model cần trình bày.
 * @returns Thẻ cảnh báo có severity và tên bảng.
 */
export function AIInsightCard({ item }: AIInsightCardProps) {
  const appearance = APPEARANCE[item.severity];
  return (
    <article
      className={`flex items-start gap-2 rounded-xl border border-l-4 p-3 text-xs ${appearance.className}`}
    >
      {appearance.icon}
      <div className="min-w-0 flex-1">
        <strong className="block text-slate-900">{item.title}</strong>
        <p className="text-slate-700">{item.description}</p>
      </div>
      <span className="whitespace-nowrap rounded-full border px-2 py-0.5 font-mono text-[10px] font-bold uppercase">
        {item.tableName}
      </span>
    </article>
  );
}
