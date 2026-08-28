"use client";

import { useTranslation } from "react-i18next";
import type { DbmlEditorMarker } from "../utils/extract-dbml-error-markers";

interface DBMLEditorScrollbarMarkersProps {
  markers: DbmlEditorMarker[];
  totalLines: number;
  onScrollToLine: (line: number) => void;
}

/** Thanh ruler hiển thị các vạch đỏ báo lỗi tại vị trí tương ứng trên thanh cuộn (như VSCode Overview Ruler). */
export function DBMLEditorScrollbarMarkers({
  markers,
  totalLines,
  onScrollToLine,
}: DBMLEditorScrollbarMarkersProps) {
  const { t } = useTranslation("modeling-workspace");
  if (markers.length === 0 || totalLines <= 0) return null;

  return (
    <aside
      aria-label={t("ARIA_ERROR_OVERVIEW_RULER")}
      className="pointer-events-none absolute right-0 top-0 bottom-0 z-20 w-3 select-none"
    >
      {markers.map((marker, idx) => {
        const topRatio = Math.max(0, Math.min((marker.line - 1) / Math.max(totalLines - 1, 1), 1));
        const topPercent = (topRatio * 100).toFixed(2);
        const localizedMessage = marker.message.startsWith("MSG_") || marker.message.startsWith("DATA_MODEL_")
          ? t(marker.message)
          : marker.message;

        return (
          <button
            key={`${marker.line}-${marker.column}-${idx}`}
            type="button"
            title={t("TOOLTIP_ERROR_LINE", { line: marker.line, message: localizedMessage })}
            onClick={() => onScrollToLine(marker.line)}
            className="pointer-events-auto absolute right-0.5 h-1.5 w-2 -translate-y-1/2 cursor-pointer rounded-xs bg-rose-500 shadow-xs ring-1 ring-rose-300 transition-all hover:h-2 hover:w-2.5 hover:bg-rose-600 dark:bg-rose-500 dark:ring-rose-900"
            style={{ top: `${topPercent}%` }}
          />
        );
      })}
    </aside>
  );
}
