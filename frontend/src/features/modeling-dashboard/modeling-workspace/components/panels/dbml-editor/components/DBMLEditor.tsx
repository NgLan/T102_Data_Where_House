"use client";

import { useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Textarea } from "@/common/components/ui/textarea";
import { useDbmlTableHighlight } from "../hooks/use-dbml-table-highlight";
import type { DBMLEditorProps, DbmlHighlightTarget } from "../types/dbml-editor-types";
import { parseDbml } from "../../../../model-document/dbml/dbml-adapter";
import { extractDbmlErrorMarkers } from "../utils/extract-dbml-error-markers";
import { findTableBlockRange } from "../utils/find-table-block-range";
import { DBMLEditorBackdrop } from "./DBMLEditorBackdrop";
import { DBMLEditorFooter } from "./DBMLEditorFooter";
import { DBMLEditorHeader } from "./DBMLEditorHeader";
import { DBMLEditorScrollbarMarkers } from "./DBMLEditorScrollbarMarkers";

const LINE_HEIGHT_PX = 24;

export { findTableBlockRange, type DbmlHighlightTarget, type DBMLEditorProps };

/** Hiển thị DBML source editor với gạch chân đỏ wavy lỗi và vạch đỏ trên thanh scroll. */
export function DBMLEditor({
  code,
  parseError,
  syntaxErrors,
  validationIssues,
  onChange,
  selectedTableName,
  highlightTarget,
  proposalReview,
}: DBMLEditorProps) {
  const { t } = useTranslation("modeling-workspace");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);

  useDbmlTableHighlight({
    code,
    selectedTableName,
    highlightTarget,
    textareaRef,
  });

  const markers = useMemo(() => {
    const directParsed = parseDbml(code);
    const effectiveSyntaxErrors =
      syntaxErrors && syntaxErrors.length > 0
        ? syntaxErrors
        : (directParsed.syntaxErrors ?? []);
    return extractDbmlErrorMarkers({
      code,
      syntaxErrors: effectiveSyntaxErrors,
      parseError: parseError || directParsed.error,
      validationIssues,
    });
  }, [code, syntaxErrors, parseError, validationIssues]);

  const totalLines = useMemo(() => code.split("\n").length, [code]);

  const handleScroll = () => {
    if (!textareaRef.current || !backdropRef.current) return;
    backdropRef.current.scrollTop = textareaRef.current.scrollTop;
    backdropRef.current.scrollLeft = textareaRef.current.scrollLeft;
  };

  const handleScrollToLine = (line: number) => {
    if (!textareaRef.current) return;
    textareaRef.current.scrollTop = Math.max(0, (line - 1) * LINE_HEIGHT_PX - 40);
    textareaRef.current.focus();
  };

  if (proposalReview) {
    return (
      <section className="relative flex h-full min-h-0 w-full flex-col overflow-hidden bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        {proposalReview}
      </section>
    );
  }

  return (
    <section className="relative flex h-full min-h-0 w-full flex-col bg-amber-50/40 text-slate-800 dark:bg-slate-950 dark:text-slate-200">
      <DBMLEditorHeader code={code} />
      <div className="relative min-h-0 flex-1 overflow-hidden">
        <DBMLEditorBackdrop ref={backdropRef} code={code} markers={markers} />
        <Textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => onChange(e.target.value)}
          onScroll={handleScroll}
          spellCheck={false}
          aria-label={t("TXT_DBML_EDITOR")}
          aria-invalid={Boolean(parseError)}
          className="light-scrollbar relative z-10 h-full min-h-0 w-full resize-none rounded-none border-0 bg-transparent p-4 font-mono text-xs leading-6 text-amber-950 focus-visible:ring-0 dark:text-sky-200 dark:dark-scrollbar"
        />
        <DBMLEditorScrollbarMarkers
          markers={markers}
          totalLines={totalLines}
          onScrollToLine={handleScrollToLine}
        />
      </div>
      <DBMLEditorFooter parseError={parseError} />
    </section>
  );
}
