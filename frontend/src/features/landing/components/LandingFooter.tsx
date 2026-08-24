"use client";

import Image from "next/image";
import { useTranslation } from "react-i18next";

/** Footer chân trang cho Landing Page. */
export function LandingFooter() {
  const { t } = useTranslation("landing");

  return (
    <footer className="border-t bg-card py-12 text-card-foreground">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3 text-center sm:text-left">
          <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white p-0.5 shadow-xs border border-gray-200">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={36}
              height={36}
              className="size-full object-contain"
            />
          </span>
          <div>
            <p className="font-semibold text-sm">{t("TXT_BRAND_NAME")}</p>
            <p className="text-xs text-muted-foreground">{t("TXT_FOOTER_TAGLINE")}</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-muted-foreground">
          <a href="#features" className="hover:text-foreground transition-colors">
            {t("TXT_FEATURES_BADGE")}
          </a>
          <a href="#demo" className="hover:text-foreground transition-colors">
            {t("TXT_DEMO_TITLE")}
          </a>
          <a href="#docs" className="hover:text-foreground transition-colors">
            {t("TXT_DOCS_BADGE")}
          </a>
        </div>

        <p className="text-xs text-muted-foreground text-center sm:text-right">
          {t("TXT_FOOTER_COPYRIGHT")}
        </p>
      </div>
    </footer>
  );
}
