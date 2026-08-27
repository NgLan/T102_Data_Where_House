"use client";

import { useId } from "react";

/** Render lưới ma trận tọa độ kỹ thuật số SVG với các điểm giao cắt chấm đỏ. */
export function TechGridSvg() {
  const patternId = useId();

  return (
    <svg className="absolute inset-0 h-full w-full stroke-neutral-900/[0.08] dark:stroke-white/[0.08] [mask-image:radial-gradient(ellipse_80%_70%_at_50%_50%,#000_70%,transparent_100%)]">
      <defs>
        <pattern id={patternId} width="40" height="40" patternUnits="userSpaceOnUse" x="-1" y="-1">
          <path d="M.5 40V.5H40" fill="none" strokeWidth="1" />
          <circle cx="0.5" cy="0.5" r="1.5" className="fill-red-500/40 dark:fill-red-400/50" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" strokeWidth="0" fill={`url(#${patternId})`} />
    </svg>
  );
}
