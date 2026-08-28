"use client";

import { useRef } from "react";
import { useTranslation } from "react-i18next";
import { Textarea } from "@/common/components/ui/textarea";
import { useDbmlTableHighlight } from "../hooks/use-dbml-table-highlight";
import type { DBMLEditorProps, DbmlHighlightTarget } from "../types/dbml-editor-types";
import { findTableBlockRange } from "../utils/find-table-block-range";
import { DBMLEditorFooter } from "./DBMLEditorFooter";
import { DBMLEditorHeader } from "./DBMLEditorHeader";

export { findTableBlockRange, type DbmlHighlightTarget, type DBMLEditorProps };

/** Hiển thị DBML source editor hoặc giao diện DBML đề xuất khi có proposal review. */
export function DBMLEditor({
  code,
  parseError,
  onChange,
  selectedTableName,
  highlightTarget,
  proposalReview,
}: DBMLEditorProps) {
  const { t } = useTranslation("modeling-workspace");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useDbmlTableHighlight({
    code,
    selectedTableName,
    highlightTarget,
    textareaRef,
  });

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
      <Textarea
        ref={textareaRef}
        value={code}
        onChange={(event) => onChange(event.target.value)}
        spellCheck={false}
        aria-label={t("TXT_DBML_EDITOR")}
        aria-invalid={Boolean(parseError)}
        className="light-scrollbar min-h-0 flex-1 resize-none rounded-none border-0 bg-amber-50/30 p-4 font-mono text-xs leading-6 text-amber-950 focus-visible:ring-0 dark:bg-slate-950 dark:text-sky-200 dark:dark-scrollbar"
      />
      <DBMLEditorFooter parseError={parseError} />
    </section>
  );
}
