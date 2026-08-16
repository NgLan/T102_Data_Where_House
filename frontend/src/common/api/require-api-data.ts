/** Bảo đảm success envelope từ generated SDK luôn chứa payload bắt buộc.
 * @param response Success envelope đã được generated SDK giải mã.
 * @returns Payload khác null của response.
 * @throws Error khi Backend trả success envelope thiếu payload.
 */
export function requireApiData<T>(response: { data?: T | null }): T {
  if (response.data == null) throw new Error("INVALID_API_RESPONSE");
  return response.data;
}
