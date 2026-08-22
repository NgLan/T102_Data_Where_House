/** Lấy payload nullable từ success envelope của generated SDK.
 * @param response Success envelope đã được generated SDK giải mã.
 * @returns Payload hoặc `null` khi Backend không trả dữ liệu.
 */
export function unwrapApiData<T>(response: { data?: T | null }): T | null {
  return response.data ?? null;
}

/** Bảo đảm success envelope từ generated SDK chứa payload bắt buộc.
 * @param response Success envelope đã được generated SDK giải mã.
 * @returns Payload khác null của response.
 * @throws Error khi Backend trả success envelope thiếu payload.
 */
export function requireApiData<T>(response: { data?: T | null }): T {
  const data = unwrapApiData(response);
  if (data === null) throw new Error("INVALID_API_RESPONSE");
  return data;
}
