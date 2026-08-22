"use client";

import { CircleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";

interface RuntimeErrorFallbackProps {
  onRetry: () => void;
}

/** Hiển thị fallback an toàn cho lỗi render mà không lộ chi tiết kỹ thuật. */
export function RuntimeErrorFallback({ onRetry }: RuntimeErrorFallbackProps) {
  const { t: tCommon } = useTranslation("common");
  const { t: tNotifications } = useTranslation("notifications");
  return (
    <main className="grid min-h-screen place-items-center bg-background p-6 text-foreground">
      <section className="w-full max-w-md rounded-xl border bg-card p-8 text-center shadow-sm">
        <CircleAlert className="mx-auto size-10 text-red-600" />
        <h1 className="mt-4 text-xl font-semibold text-foreground">
          {tNotifications("TXT_RUNTIME_ERROR_TITLE")}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {tNotifications("TXT_RUNTIME_ERROR_DESCRIPTION")}
        </p>
        <Button type="button" className="mt-6" onClick={onRetry}>
          {tCommon("BTN_RETRY")}
        </Button>
      </section>
    </main>
  );
}
