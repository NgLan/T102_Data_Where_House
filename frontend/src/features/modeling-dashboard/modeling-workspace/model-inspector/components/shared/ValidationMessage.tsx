import { useTranslation } from "react-i18next";

interface ValidationMessageProps {
  code?: string;
}

/** Hiển thị lỗi validation theo translation key.
 * @param props Mã lỗi tùy chọn của field.
 * @returns Thông báo lỗi hoặc null khi field hợp lệ.
 */
export function ValidationMessage({ code }: ValidationMessageProps) {
  const { t } = useTranslation("modeling-dashboard");
  return code ? (
    <p className="text-xs text-destructive" role="alert">
      {t(code)}
    </p>
  ) : null;
}
