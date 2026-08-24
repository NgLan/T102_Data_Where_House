"use client";

import { useTranslation } from "react-i18next";
import { Badge } from "@/common/components/ui/badge";
import { Button } from "@/common/components/ui/button";
import { ExternalLink, FileText, ShieldCheck, Code2, AlertCircle } from "lucide-react";

/** Section hiển thị đường dẫn liên kết tài liệu hướng dẫn (Doc Link Placeholder) và xem trước các chủ đề. */
export function DocsSection() {
  const { t } = useTranslation("landing");

  return (
    <section id="docs" className="relative z-10 py-16 border-t bg-background/60 backdrop-blur-[1px]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <Badge variant="secondary" className="mb-3">
            {t("TXT_DOCS_BADGE")}
          </Badge>
          <h2 className="text-2xl font-bold sm:text-4xl text-foreground">
            {t("TXT_DOCS_TITLE")}
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            {t("TXT_DOCS_SUBTITLE")}
          </p>
        </div>

        {/* Doc Link Placeholder Banner */}
        <div className="mb-10 rounded-2xl border border-primary/20 bg-primary/5 p-6 text-center sm:flex sm:items-center sm:justify-between sm:text-left">
          <div className="space-y-1 mb-4 sm:mb-0">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <Badge variant="outline" className="border-primary/40 text-primary gap-1">
                <AlertCircle className="size-3" />
                <span>{t("TXT_DOCS_PLACEHOLDER_BADGE")}</span>
              </Badge>
            </div>
            <p className="text-sm text-foreground font-medium mt-1">
              {t("TXT_DOCS_PLACEHOLDER_NOTE")}
            </p>
          </div>

          <Button
            asChild
            variant="default"
            className="cursor-pointer gap-2 shrink-0 font-semibold"
          >
            <a
              href="https://docs.example.com"
              target="_blank"
              rel="noopener noreferrer"
              title="Documentation Placeholder Link"
            >
              <ExternalLink className="size-4" />
              <span>{t("BTN_DOCS_GO_TO_LINK")}</span>
            </a>
          </Button>
        </div>

        {/* Preview Doc Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border bg-card p-6 shadow-sm hover:border-primary/50 transition-colors">
            <div className="size-10 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
              <FileText className="size-5" />
            </div>
            <h3 className="font-semibold text-foreground text-base mb-2">
              {t("TXT_DOCS_CARD_1_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_DOCS_CARD_1_DESC")}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm hover:border-primary/50 transition-colors">
            <div className="size-10 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
              <ShieldCheck className="size-5" />
            </div>
            <h3 className="font-semibold text-foreground text-base mb-2">
              {t("TXT_DOCS_CARD_2_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_DOCS_CARD_2_DESC")}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm hover:border-primary/50 transition-colors">
            <div className="size-10 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
              <Code2 className="size-5" />
            </div>
            <h3 className="font-semibold text-foreground text-base mb-2">
              {t("TXT_DOCS_CARD_3_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_DOCS_CARD_3_DESC")}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
