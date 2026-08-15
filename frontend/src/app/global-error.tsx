"use client";

import { RuntimeErrorFallback } from "@/common/components/errors/RuntimeErrorFallback";
import { I18nProvider } from "@/common/i18n/I18nProvider";
import i18n from "@/common/i18n/i18n";
import "./globals.css";

interface GlobalErrorProps {
  error: Error & { digest?: string };
  retry: () => void;
}

/** Bắt lỗi của root layout và tự dựng lại document theo quy ước Next.js. */
export default function GlobalError({
  retry,
}: GlobalErrorProps) {
  return (
    <html lang={i18n.resolvedLanguage ?? "vi"}>
      <body>
        <title>{i18n.t("TXT_RUNTIME_ERROR_TITLE", { ns: "notifications" })}</title>
        <I18nProvider>
          <RuntimeErrorFallback onRetry={retry} />
        </I18nProvider>
      </body>
    </html>
  );
}
