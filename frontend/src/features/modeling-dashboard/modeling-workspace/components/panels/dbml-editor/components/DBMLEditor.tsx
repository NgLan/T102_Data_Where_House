"use client";

import { Check, Code2, Copy } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { copyTextToClipboard } from "@/common/browser/copy-text-to-clipboard";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";

const COPY_CONFIRMATION_DURATION_MS = 1500;

interface DBMLEditorProps {
  code: string;
  parseError: string | null;
  onChange: (value: string) => void;
  selectedTableName?: string | null;
  proposalReview?: ReactNode;
}

/** Hiển thị DBML source editor hoặc giao diện DBML đề xuất khi có proposal review. */
export function DBMLEditor({
  code,
  parseError,
  onChange,
  selectedTableName,
  proposalReview,
}: DBMLEditorProps) {
  const { t } = useTranslation("modeling-workspace");
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!selectedTableName) return;
    const lines = code.split("\n");
    const escapedName = selectedTableName.replace(
      /[.*+?^${}()|[\]\\]/g,
      "\\$&",
    );
    const tableRegex = new RegExp(
      `^\\s*Table\\s+(?:[a-zA-Z0-9_"]+\\.)?["']?${escapedName}["']?\\b`,
      "i",
    );
    const lineIndex = lines.findIndex((line) => tableRegex.test(line));
    if (lineIndex < 0) return;

    const startPos =
      lines.slice(0, lineIndex).join("\n").length + (lineIndex > 0 ? 1 : 0);
    const endPos = startPos + lines[lineIndex].length;

    const textarea = textareaRef.current;
    if (textarea) {
      textarea.focus();
      textarea.setSelectionRange(startPos, endPos);
      const lineHeight = 24;
      const scrollTop = Math.max(0, lineIndex * lineHeight - 40);
      textarea.scrollTop = scrollTop;
    }
  }, [selectedTableName, code]);

  const handleCopy = async () => {
    if (!(await copyTextToClipboard(code))) return;
    setCopied(true);
    window.setTimeout(() => setCopied(false), COPY_CONFIRMATION_DURATION_MS);
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
      <header className="flex items-center gap-2 border-b border-amber-200/80 bg-amber-100/50 px-3 py-2 text-slate-900 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-100">
        <Code2
          className="size-4 text-amber-600 dark:text-sky-400"
          aria-hidden="true"
        />
        <strong className="mr-auto text-xs font-semibold text-slate-900 dark:text-slate-100">
          {t("TXT_DBML_EDITOR")}
        </strong>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={() => void handleCopy()}
          className="border border-amber-300 bg-white text-amber-900 hover:bg-amber-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          {copied ? (
            <Check className="size-3.5" />
          ) : (
            <Copy className="size-3.5" />
          )}
          {copied ? t("BTN_COPIED") : t("BTN_COPY")}
        </Button>
      </header>
      <Textarea
        ref={textareaRef}
        value={code}
        onChange={(event) => onChange(event.target.value)}
        spellCheck={false}
        aria-label={t("TXT_DBML_EDITOR")}
        aria-invalid={Boolean(parseError)}
        className="light-scrollbar min-h-0 flex-1 resize-none rounded-none border-0 bg-amber-50/30 p-4 font-mono text-xs leading-6 text-amber-950 focus-visible:ring-0 dark:bg-slate-950 dark:text-sky-200 dark:dark-scrollbar"
      />
      <footer
        className={`border-t px-3 py-1.5 text-[11px] font-medium ${
          parseError
            ? "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950/60 dark:text-rose-300"
            : "border-amber-200/80 bg-amber-100/50 text-amber-800 dark:border-slate-800 dark:bg-slate-900/60 dark:text-emerald-400"
        }`}
      >
        {parseError ? t("MSG_DBML_INVALID") : t("MSG_DBML_SYNCED")}
      </footer>
    </section>
  );
}
