import { useTranslation } from "react-i18next";
import { FolderKanban } from "lucide-react";

/** Hiển thị phần giới thiệu tinh gọn của Project Management theo phong cách Modern SaaS.
 * @returns Header có icon, tiêu đề và mô tả gọn gàng, không chiếm dụng không gian.
 */
export function ProjectManagementHero() {
  const { t } = useTranslation("project-management");
  return (
    <header className="flex flex-col gap-1 border-b pb-4">
      <div className="flex items-center gap-2.5">
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <FolderKanban className="size-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {t("TXT_TITLE")}
          </h1>
        </div>
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        {t("TXT_SUBTITLE")}
      </p>
    </header>
  );
}
