import { ShieldCheck } from "lucide-react";
import { useTranslation } from "react-i18next";

/** Notice luôn bật theo data flow: PII Guard nằm giữa Agent và LLM.
 * @returns Thông báo về lớp bảo vệ dữ liệu nhạy cảm.
 */
export function PiiGuardNotice() {
  const { t } = useTranslation("project-init");
  return <aside className="flex gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-950">
    <ShieldCheck className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
    <div>
      <p className="text-sm font-semibold">{t("TXT_PII_GUARD_TITLE")}</p>
      <p className="mt-1 text-xs text-emerald-800">{t("TXT_PII_GUARD_DESCRIPTION")}</p>
    </div>
  </aside>;
}
