"use client";

import Link from "next/link";
import Image from "next/image";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { LanguageSwitcher } from "@/common/components/layout/LanguageSwitcher";
import { ThemeSwitcher } from "@/common/components/layout/ThemeSwitcher";
import { LogIn } from "lucide-react";

interface LandingHeaderProps {
  onLoginClick?: () => void;
}

/** Header điều hướng cho trang Landing Page với nút Đăng nhập nổi bật.
 * @param props Callback kích hoạt khi bấm nút Đăng nhập.
 */
export function LandingHeader({ onLoginClick }: LandingHeaderProps) {
  const { t } = useTranslation("landing");

  return (
    <header className="sticky top-0 z-40 shrink-0 border-b bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link
          href="/"
          className="flex cursor-pointer shrink-0 items-center gap-2.5 rounded-md font-bold text-foreground transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <span className="flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-white p-0.5 shadow-xs border border-gray-200">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={40}
              height={40}
              className="size-full object-contain scale-110"
              priority
            />
          </span>
          <span className="text-base font-bold sm:text-lg tracking-tight">
            {t("TXT_BRAND_NAME")}
          </span>
        </Link>

        <nav aria-label="Landing navigation" className="hidden md:flex items-center gap-6 text-sm font-medium text-muted-foreground">
          <a href="#features" className="transition-colors hover:text-foreground">
            {t("TXT_FEATURES_BADGE")}
          </a>
          <a href="#demo" className="transition-colors hover:text-foreground">
            {t("TXT_DEMO_TITLE")}
          </a>
          <a href="#docs" className="transition-colors hover:text-foreground">
            {t("TXT_DOCS_BADGE")}
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <ThemeSwitcher />
          <Button
            asChild
            variant="default"
            className="cursor-pointer gap-2 shadow-sm font-semibold"
          >
            <Link href="/auth" onClick={onLoginClick}>
              <LogIn className="size-4" />
              <span>{t("BTN_LOGIN")}</span>
            </Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
