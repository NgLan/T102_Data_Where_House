import { useTranslation } from "react-i18next";

/** Hiển thị phần giới thiệu của Project Management.
 * @returns Hero có eyebrow, tiêu đề và mô tả đã i18n.
 */
export function ProjectManagementHero() {
  const { t } = useTranslation("project-management");
  return (
    <header className="rounded-2xl bg-primary p-8 text-primary-foreground shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wider opacity-75">
        {t("TXT_EYEBROW")}
      </p>
      <h1 className="mt-2 text-2xl font-bold">{t("TXT_TITLE")}</h1>
      <p className="mt-2 max-w-2xl text-sm opacity-75">{t("TXT_SUBTITLE")}</p>
    </header>
  );
}
