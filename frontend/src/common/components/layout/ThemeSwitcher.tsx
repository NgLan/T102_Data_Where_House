"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";

/** Chuyển giữa light và dark theme, có xét system theme ban đầu.
 * @returns Nút icon thay đổi theme hiện hành.
 */
export function ThemeSwitcher() {
  const { resolvedTheme, setTheme } = useTheme();
  const { t } = useTranslation("common");
  const handleSwitchTheme = () => setTheme(resolvedTheme === "dark" ? "light" : "dark");
  return (
    <Button variant="ghost" size="icon" onClick={handleSwitchTheme}
      aria-label={t("BTN_SWITCH_THEME")} title={t("BTN_SWITCH_THEME")}>
      <Sun className="dark:hidden" aria-hidden />
      <Moon className="hidden dark:block" aria-hidden />
    </Button>
  );
}
