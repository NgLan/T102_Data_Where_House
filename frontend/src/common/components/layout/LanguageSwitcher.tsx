"use client";

import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";

/** Chuyển nhanh giữa hai locale VI và EN.
 * @returns Nút đổi sang locale còn lại.
 * @remarks I18nProvider chịu trách nhiệm lưu locale và cập nhật thuộc tính lang.
 */
export function LanguageSwitcher() {
  const { i18n, t } = useTranslation("common");
  const isVietnamese = i18n.resolvedLanguage?.startsWith("vi") ?? true;
  const nextLanguage = isVietnamese ? "en" : "vi";
  const handleSwitchLanguage = () => { void i18n.changeLanguage(nextLanguage); };
  return (
    <Button variant="ghost" size="sm" onClick={handleSwitchLanguage}
      aria-label={t("BTN_SWITCH_LANGUAGE")} title={t("BTN_SWITCH_LANGUAGE")}>
      <Languages aria-hidden />
      <span className="hidden sm:inline">{nextLanguage.toUpperCase()}</span>
    </Button>
  );
}
