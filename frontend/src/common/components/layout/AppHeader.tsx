"use client";

import Link from "next/link";
import { DatabaseZap } from "lucide-react";
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
        <Link href="/" className="flex cursor-pointer shrink-0 items-center gap-2 rounded-md font-semibold
          text-foreground transition-colors hover:text-primary focus-visible:outline-none
          focus-visible:ring-2 focus-visible:ring-ring">
          <span className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground">
            <DatabaseZap className="size-4" aria-hidden />
          </span>
          <span className="hidden lg:inline">{t("TXT_APP_NAME")}</span>
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
