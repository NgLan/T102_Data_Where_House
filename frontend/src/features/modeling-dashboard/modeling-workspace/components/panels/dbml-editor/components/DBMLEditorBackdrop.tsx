"use client";

import { forwardRef } from "react";
import { useTranslation } from "react-i18next";
import type { DbmlEditorMarker } from "../utils/extract-dbml-error-markers";

const WAVY_SQUIGGLE_SVG =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 6 3' width='6' height='3'%3E%3Cpath d='M0 2.5 Q 1.5 0.5, 3 2.5 T 6 2.5' fill='none' stroke='%23ef4444' stroke-width='1.2' stroke-linecap='round'/%3E%3C/svg%3E\")";

interface DBMLEditorBackdropProps {
  code: string;
  markers: DbmlEditorMarker[];
}

/** Lớp phủ render gạch chân lượn sóng đỏ (wavy squiggly) trực tiếp dưới từng chữ bị lỗi như VSCode. */
export const DBMLEditorBackdrop = forwardRef<HTMLDivElement, DBMLEditorBackdropProps>(
  function DBMLEditorBackdrop({ code, markers }, ref) {
    const { t } = useTranslation("modeling-workspace");
    const lines = code.split("\n");
    const markersByLine = new Map<number, DbmlEditorMarker>();
    for (const m of markers) {
      if (!markersByLine.has(m.line)) markersByLine.set(m.line, m);
    }

    return (
      <div
        ref={ref}
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-20 overflow-hidden whitespace-pre p-4 font-mono text-xs leading-6 select-none"
      >
        {lines.map((lineText, idx) => {
          const lineNum = idx + 1;
          const marker = markersByLine.get(lineNum);

          if (!marker || !lineText) {
            return (
              <div key={lineNum} className="h-6 text-transparent">
                {lineText || "\u00A0"}
              </div>
            );
          }

          const start = Math.max(0, marker.column - 1);
          const end = Math.min(lineText.length, Math.max(marker.endColumn - 1, start + 1));
          const before = lineText.slice(0, start);
          const errorPart = lineText.slice(start, end) || lineText.trim() || "\u00A0";
          const after = lineText.slice(end);
          const localizedTooltip = marker.message.startsWith("MSG_") || marker.message.startsWith("DATA_MODEL_")
            ? t(marker.message)
            : marker.message;

          return (
            <div
              key={lineNum}
              className="h-6 -mx-4 px-4 bg-rose-500/10 text-transparent border-l-2 border-rose-500 transition-colors"
            >
              {before}
              <span
                className="inline-block text-transparent bg-bottom bg-repeat-x pb-[2px]"
                style={{
                  backgroundImage: WAVY_SQUIGGLE_SVG,
                  backgroundSize: "6px 3px",
                }}
                title={localizedTooltip}
              >
                {errorPart}
              </span>
              {after}
            </div>
          );
        })}
      </div>
    );
  },
);
