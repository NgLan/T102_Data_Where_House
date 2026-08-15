"use client";

import { Check, Code2, Copy } from "lucide-react";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";
import {
  MAX_DBML_EDITOR_WIDTH_PX,
  MIN_DBML_EDITOR_WIDTH_PX,
  useResizableDBMLEditor,
} from "../hooks/use-resizable-dbml-editor";

const COPY_CONFIRMATION_DURATION_MS = 1500;

interface DBMLEditorProps {
  code: string;
  parseError: string | null;
  onChange: (value: string) => void;
  selectedTableName?: string | null;
}

/** Hiển thị DBML source editor là một nửa nguồn chỉnh sửa của canonical draft.
 * @param props DBML source, parse error và callback cập nhật.
 * @returns Editor tối, có copy và trạng thái parse.
 */
export function DBMLEditor({
  code,
  parseError,
  onChange,
  selectedTableName,
}: DBMLEditorProps) {
  const { t } = useTranslation("modeling-dashboard");
  const [copied, setCopied] = useState(false);
  const resize = useResizableDBMLEditor();
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
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), COPY_CONFIRMATION_DURATION_MS);
  };
  return (
    <section
      style={{ "--dbml-editor-width": `${resize.width}px` } as CSSProperties}
      className="relative flex min-h-0 w-full flex-1 flex-col bg-slate-950 text-slate-200 lg:h-full lg:w-[var(--dbml-editor-width)] lg:flex-none"
    >
      <header className="flex items-center gap-2 border-b border-slate-800 px-3 py-2">
        <Code2 className="size-4 text-sky-400" aria-hidden="true" />
        <strong className="mr-auto text-xs">{t("TXT_DBML_EDITOR")}</strong>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={() => void handleCopy()}
        >
          {copied ? <Check /> : <Copy />}
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
        className="min-h-0 flex-1 resize-none rounded-none border-0 bg-slate-950 p-4 font-mono text-xs leading-6 text-sky-200 focus-visible:ring-0"
      />
      <footer
        className={`border-t px-3 py-1.5 text-[11px] ${parseError ? "border-red-900 bg-red-950 text-red-300" : "border-slate-800 text-emerald-400"}`}
      >
        {parseError ? t("MSG_DBML_INVALID") : t("MSG_DBML_SYNCED")}
      </footer>
      <div
        role="separator"
        aria-label={t("BTN_RESIZE_DBML_EDITOR")}
        aria-orientation="vertical"
        aria-valuemin={MIN_DBML_EDITOR_WIDTH_PX}
        aria-valuemax={MAX_DBML_EDITOR_WIDTH_PX}
        aria-valuenow={resize.width}
        tabIndex={0}
        onPointerDown={resize.handlePointerDown}
        onPointerMove={resize.handlePointerMove}
        onPointerUp={resize.handlePointerUp}
        onKeyDown={resize.handleKeyDown}
        className="absolute inset-y-0 right-0 z-20 hidden w-1 translate-x-1/2 cursor-col-resize touch-none bg-transparent outline-none transition-colors hover:bg-blue-400 focus-visible:bg-blue-400 lg:block"
      />
    </section>
  );
}
