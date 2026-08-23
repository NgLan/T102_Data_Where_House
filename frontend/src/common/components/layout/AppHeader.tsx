"use client";

import Link from "next/link";
import Image from "next/image";
import { useTranslation } from "react-i18next";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { ProjectSwitcher } from "./ProjectSwitcher";
import { ThemeSwitcher } from "./ThemeSwitcher";
import { UserMenu } from "./UserMenu";

interface AppHeaderProps {
  selectedProjectId?: string;
}

/** Header dùng chung cho mọi màn hình nghiệp vụ.
 * @param props Project hiện hành để đồng bộ project switcher.
 * @returns Header gồm logo, project, locale, theme và actor menu.
 */
export function AppHeader({ selectedProjectId }: AppHeaderProps) {
  const { t } = useTranslation("common");
  return (
    <header className="z-40 shrink-0 border-b bg-background/90 backdrop-blur-md">
      <div className="flex min-h-14 items-center gap-2 px-3 sm:gap-4 sm:px-6">
        <Link href="/" className="flex cursor-pointer shrink-0 items-center gap-2.5 rounded-md font-bold
          text-foreground transition-colors hover:text-primary focus-visible:outline-none
          focus-visible:ring-2 focus-visible:ring-ring">
          <span className="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-white p-0.5 shadow-xs border border-gray-200">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={44}
              height={44}
              className="size-full object-contain scale-110"
              priority
            />
          </span>
          <span className="hidden text-base font-bold sm:inline md:text-lg tracking-tight">{t("TXT_APP_NAME")}</span>
        </Link>
        <ProjectSwitcher selectedProjectId={selectedProjectId} />
        <nav className="ml-auto flex shrink-0 items-center gap-1" aria-label={t("TXT_HEADER_ACTIONS")}>
          <LanguageSwitcher />
          <ThemeSwitcher />
          <UserMenu />
        </nav>
      </div>
    </header>
  );
}
