"use client";

import { Check, Code2, Copy } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { copyTextToClipboard } from "@/common/browser/copy-text-to-clipboard";
import { Button } from "@/common/components/ui/button";

const COPY_FEEDBACK_MS = 1500;

interface DBMLEditorHeaderProps {
  code: string;
}

/** Header của DBML Editor với tiêu đề và nút sao chép mã nguồn. */
export function DBMLEditorHeader({ code }: DBMLEditorHeaderProps) {
  const { t } = useTranslation("modeling-workspace");
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!(await copyTextToClipboard(code))) return;
    setCopied(true);
    window.setTimeout(() => setCopied(false), COPY_FEEDBACK_MS);
  };

  return (
    <header className="flex items-center gap-2 border-b border-amber-200/80 bg-amber-100/50 px-3 py-2 text-slate-900 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-100">
      <Code2 className="size-4 text-amber-600 dark:text-sky-400" aria-hidden="true" />
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
        {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
        {copied ? t("BTN_COPIED") : t("BTN_COPY")}
      </Button>
    </header>
  );
}
