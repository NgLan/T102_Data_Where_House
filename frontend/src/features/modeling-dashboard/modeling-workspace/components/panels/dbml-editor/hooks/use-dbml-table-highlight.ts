import { useEffect, useRef, type RefObject } from "react";
import type { DbmlHighlightTarget } from "../types/dbml-editor-types";
import { findTableBlockRange } from "../utils/find-table-block-range";

const HIGHLIGHT_DURATION_MS = 1500;
const LINE_HEIGHT_PX = 24;

interface UseDbmlTableHighlightOptions {
  code: string;
  selectedTableName?: string | null;
  highlightTarget?: DbmlHighlightTarget | null;
  textareaRef: RefObject<HTMLTextAreaElement | null>;
}

/** Hook quản lý cuộn đến bảng, bôi chọn toàn bộ khối DBML và tự động giải phóng focus. */
export function useDbmlTableHighlight({
  code,
  selectedTableName,
  highlightTarget,
  textareaRef,
}: UseDbmlTableHighlightOptions): void {
  const highlightTimerRef = useRef<number | null>(null);
  const targetName = highlightTarget?.tableName ?? selectedTableName;
  const triggerKey = highlightTarget
    ? `${highlightTarget.tableName}:${highlightTarget.triggerAt}`
    : selectedTableName;

  useEffect(() => {
    if (!targetName) return;
    const range = findTableBlockRange(code, targetName);
    const textarea = textareaRef.current;
    if (!range || !textarea) return;

    textarea.scrollTop = Math.max(0, range.lineIndex * LINE_HEIGHT_PX - 40);
    textarea.focus({ preventScroll: true });
    textarea.setSelectionRange(range.startPos, range.endPos);

    if (highlightTimerRef.current) window.clearTimeout(highlightTimerRef.current);
    highlightTimerRef.current = window.setTimeout(() => {
      clearSelectionAndBlur(textareaRef.current);
    }, HIGHLIGHT_DURATION_MS);

    return () => {
      if (highlightTimerRef.current) window.clearTimeout(highlightTimerRef.current);
    };
  }, [triggerKey]);
}

/** Hủy vùng chọn và xóa focus để không bị khóa trỏ chuột trong editor. */
function clearSelectionAndBlur(textarea: HTMLTextAreaElement | null): void {
  if (!textarea) return;
  const end = textarea.selectionEnd;
  textarea.setSelectionRange(end, end);
  if (document.activeElement === textarea) {
    textarea.blur();
  }
}
