"use client";

import { Network } from "lucide-react";
import { useTranslation } from "react-i18next";

export function ERDEmptyState() {
  const { t } = useTranslation("modeling-workspace");
  return (
    <section className="flex h-full w-full min-h-0 flex-1 flex-col items-center justify-center gap-3 border-x bg-muted/30 p-8 text-center">
      <Network className="size-12 text-muted-foreground/50" />
      <strong>{t("TXT_EMPTY_MODEL_TITLE")}</strong>
      <p className="max-w-sm text-sm text-muted-foreground">
        {t("TXT_EMPTY_MODEL_DESCRIPTION")}
      </p>
    </section>
  );
}
