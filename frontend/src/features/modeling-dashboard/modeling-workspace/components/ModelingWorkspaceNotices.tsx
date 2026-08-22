"use client";

import { Info, Loader2, Sparkles } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Skeleton } from "@/common/components/ui/skeleton";

export function EmptyModelNotice({ onGenerate }: { onGenerate: () => void }) {
  const { t } = useTranslation("modeling-workspace");
  return (
    <div className="flex items-center gap-3 border-b bg-blue-50/70 px-4 py-2 text-xs text-blue-900">
      <Info className="size-3.5" />
      <span className="mr-auto">{t("MSG_NO_DATA_MODEL")}</span>
      <Button size="sm" onClick={onGenerate}>
        <Sparkles />
        {t("BTN_GENERATE_FROM_SOURCES")}
      </Button>
    </div>
  );
}

export function GeneratingNotice() {
  const { t } = useTranslation("modeling-workspace");
  return (
    <p
      className="flex items-center gap-2 border-b bg-blue-50/70 px-4 py-2.5 text-xs text-blue-900"
      role="status"
    >
      <Loader2 className="size-3.5 animate-spin" />
      {t("MSG_GENERATING_FROM_SOURCES")}
    </p>
  );
}

export function OutdatedModelNotice({ onUpdate }: { onUpdate: () => void }) {
  const { t } = useTranslation("modeling-workspace");
  return (
    <div className="flex items-center gap-3 border-b bg-amber-50 px-4 py-2 text-xs text-amber-900">
      <Info className="size-3.5" />
      <span className="mr-auto">{t("MSG_DATA_MODEL_OUTDATED")}</span>
      <Button size="sm" onClick={onUpdate}>
        <Sparkles />
        {t("BTN_UPDATE_DATA_MODEL")}
      </Button>
    </div>
  );
}

export function WorkspaceSkeleton() {
  const { t } = useTranslation("modeling-workspace");
  return (
    <div
      className="grid min-h-0 flex-1 gap-3 p-3 lg:grid-cols-[300px_1fr_360px]"
      aria-label={t("TXT_LOADING")}
    >
      <Skeleton className="h-full" />
      <Skeleton className="h-full" />
      <Skeleton className="h-full" />
    </div>
  );
}
