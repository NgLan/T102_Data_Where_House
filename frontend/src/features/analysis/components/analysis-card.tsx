import type { ReactNode } from "react";

import { cn } from "@/common/utils/cn";

import { Icon, type IconName } from "./icon";

type CardTone = "blue" | "emerald" | "amber";

interface AnalysisCardProps {
  id: string;
  title: string;
  eyebrow: string;
  icon: IconName;
  tone: CardTone;
  expanded: boolean;
  onToggle: () => void;
  children: ReactNode;
}

const TONE_STYLES: Record<CardTone, { icon: string; border: string }> = {
  blue: { icon: "bg-blue-50 text-blue-600", border: "border-blue-100" },
  emerald: { icon: "bg-emerald-50 text-emerald-600", border: "border-emerald-100" },
  amber: { icon: "bg-amber-50 text-amber-600", border: "border-amber-100" },
};

/** Hiển thị một nhóm diễn giải có thể mở rộng hoặc thu gọn. */
export function AnalysisCard({
  id,
  title,
  eyebrow,
  icon,
  tone,
  expanded,
  onToggle,
  children,
}: AnalysisCardProps) {
  const style = TONE_STYLES[tone];

  return (
    <section className={cn("overflow-hidden rounded-2xl border bg-white", style.border)}>
      <button
        type="button"
        className="flex w-full items-center gap-3 px-4 py-3.5 text-left transition hover:bg-slate-50/70 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-blue-600"
        aria-expanded={expanded}
        aria-controls={id}
        onClick={onToggle}
      >
        <span className={cn("grid size-9 place-items-center rounded-xl", style.icon)}>
          <Icon name={icon} className="size-[18px]" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-[10px] font-bold tracking-[0.12em] text-slate-400 uppercase">
            {eyebrow}
          </span>
          <span className="mt-0.5 block truncate text-sm font-semibold text-slate-800">
            {title}
          </span>
        </span>
        <Icon
          name="chevron"
          className={cn("size-4 text-slate-400 transition-transform", expanded && "rotate-90")}
        />
      </button>
      {expanded && (
        <div id={id} className="border-t border-slate-100 px-4 py-4">
          {children}
        </div>
      )}
    </section>
  );
}
