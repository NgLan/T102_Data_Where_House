"use client";

import { useTranslation } from "react-i18next";

interface DBMLEditorFooterProps {
  parseError: string | null;
}

/** Thanh trạng thái dưới cùng của DBML Editor báo tính hợp lệ của mã nguồn. */
export function DBMLEditorFooter({ parseError }: DBMLEditorFooterProps) {
  const { t } = useTranslation("modeling-workspace");
  const tone = parseError
    ? "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950/60 dark:text-rose-300"
    : "border-amber-200/80 bg-amber-100/50 text-amber-800 dark:border-slate-800 dark:bg-slate-900/60 dark:text-emerald-400";

  return (
    <footer className={`border-t px-3 py-1.5 text-[11px] font-medium ${tone}`}>
      {parseError ? t("MSG_DBML_INVALID") : t("MSG_DBML_SYNCED")}
    </footer>
  );
}
