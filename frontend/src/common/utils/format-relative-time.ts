export type TranslateFn = (key: string, options?: Record<string, unknown>) => string;

/** Format mốc thời gian thành chuỗi thời gian tương đối thân thiện thông qua i18n key.
 * @param dateInput Chuỗi ISO hoặc đối tượng Date.
 * @param t Hàm dịch i18n từ common.json.
 * @param locale Mã ngôn ngữ khi format lịch nếu vượt quá 7 ngày.
 * @returns Chuỗi thời gian tương đối đã được dịch i18n.
 */
export function formatRelativeTime(
  dateInput: string | Date,
  t: TranslateFn,
  locale: string = "vi",
): string {
  const targetDate = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (isNaN(targetDate.getTime())) return "";

  const diffMs = Date.now() - targetDate.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) return t("TIME_JUST_NOW");
  if (diffMinutes < 60) return t("TIME_MINUTES_AGO", { count: diffMinutes });
  if (diffHours < 24) return t("TIME_HOURS_AGO", { count: diffHours });
  if (diffDays === 1) return t("TIME_YESTERDAY");
  if (diffDays < 7) return t("TIME_DAYS_AGO", { count: diffDays });

  return formatCalendarDate(targetDate, locale);
}

/** Format ngày tháng theo lịch (ví dụ: 28/08/2026). */
export function formatCalendarDate(
  dateInput: string | Date,
  locale: string = "vi",
): string {
  const date = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

/** Format ngày giờ chi tiết dùng cho tooltip hover. */
export function formatFullDateTime(
  dateInput: string | Date,
  locale: string = "vi",
): string {
  const targetDate = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (isNaN(targetDate.getTime())) return "";

  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(targetDate);
}
