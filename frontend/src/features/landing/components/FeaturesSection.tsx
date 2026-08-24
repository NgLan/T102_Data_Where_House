"use client";

import { useTranslation } from "react-i18next";
import { Badge } from "@/common/components/ui/badge";
import { Cpu, ShieldCheck, Layers, Terminal } from "lucide-react";

/** Section danh mục các tính năng kỹ thuật nổi bật của hệ thống AIDWH. */
export function FeaturesSection() {
  const { t } = useTranslation("landing");

  return (
    <section id="features" className="relative z-10 py-16 border-t bg-muted/10 backdrop-blur-[1px]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <Badge variant="outline" className="mb-3">
            {t("TXT_FEATURES_BADGE")}
          </Badge>
          <h2 className="text-2xl font-bold sm:text-4xl text-foreground">
            {t("TXT_FEATURES_TITLE")}
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            {t("TXT_FEATURES_SUBTITLE")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center text-center">
            <div className="size-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4">
              <Cpu className="size-6" />
            </div>
            <h3 className="font-bold text-foreground text-lg mb-2">
              {t("TXT_FEATURE_1_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_FEATURE_1_DESC")}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center text-center">
            <div className="size-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4">
              <ShieldCheck className="size-6" />
            </div>
            <h3 className="font-bold text-foreground text-lg mb-2">
              {t("TXT_FEATURE_2_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_FEATURE_2_DESC")}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center text-center">
            <div className="size-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4">
              <Layers className="size-6" />
            </div>
            <h3 className="font-bold text-foreground text-lg mb-2">
              {t("TXT_FEATURE_3_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_FEATURE_3_DESC")}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center text-center">
            <div className="size-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4">
              <Terminal className="size-6" />
            </div>
            <h3 className="font-bold text-foreground text-lg mb-2">
              {t("TXT_FEATURE_4_TITLE")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t("TXT_FEATURE_4_DESC")}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
