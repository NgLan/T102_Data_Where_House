"use client";

import Link from "next/link";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Badge } from "@/common/components/ui/badge";
import { LogIn, PlayCircle, BookOpen, Sparkles } from "lucide-react";

interface HeroSectionProps {
  onLoginClick?: () => void;
}

/** Vùng Hero chính giới thiệu nền tảng tự động hóa DWH và nút CTA.
 * @param props Callback kích hoạt khi bấm nút Đăng nhập.
 */
export function HeroSection({ onLoginClick }: HeroSectionProps) {
  const { t } = useTranslation("landing");

  return (
    <section className="relative overflow-hidden py-16 md:py-24">
      <div className="pointer-events-none absolute left-1/2 top-0 -z-10 size-[500px] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative z-10 mx-auto max-w-4xl text-center">
        <Badge variant="secondary" className="mb-4 inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold">
          <Sparkles className="size-3.5 text-primary" />
          <span>{t("TXT_HERO_BADGE")}</span>
        </Badge>

        <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl md:text-6xl text-foreground">
          {t("TXT_HERO_TITLE")}
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          {t("TXT_HERO_SUBTITLE")}
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Button
            size="lg"
            asChild
            className="cursor-pointer gap-2 px-6 py-6 text-base font-semibold shadow-md"
          >
            <Link href="/auth" onClick={onLoginClick}>
              <LogIn className="size-5" />
              <span>{t("BTN_LOGIN")}</span>
            </Link>
          </Button>

          <Button
            size="lg"
            variant="outline"
            asChild
            className="cursor-pointer gap-2 px-6 py-6 text-base font-semibold"
          >
            <a href="#demo">
              <PlayCircle className="size-5 text-primary" />
              <span>{t("BTN_WATCH_DEMO")}</span>
            </a>
          </Button>

          <Button
            size="lg"
            variant="ghost"
            asChild
            className="cursor-pointer gap-2 px-4 py-6 text-base font-semibold"
          >
            <a href="#docs">
              <BookOpen className="size-5 text-muted-foreground" />
              <span>{t("BTN_EXPLORE_DOCS")}</span>
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
}
