/** Chọn bản dịch Backend ErrorCode hoặc fallback đã dịch. */
export function resolveErrorMessage(
  translatedMessage: string,
  fallbackMessage: string,
): string {
  return translatedMessage || fallbackMessage;
}
