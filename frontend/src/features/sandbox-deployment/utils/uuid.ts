/**
 * Utility: Kiểm tra và sinh mã định danh UUID v4 chuẩn
 * Phục vụ đồng bộ định danh giữa Frontend và Backend CSDL.
 */

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/**
 * Kiểm tra xem một giá trị có phải là chuỗi UUID hợp lệ hay không
 */
export function isValidUuid(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  return UUID_REGEX.test(value.trim());
}

/**
 * Sinh UUID v4 tạm thời trên trình duyệt (sử dụng Web Crypto API)
 */
export function generateTempUuid(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // Fallback an toàn cho môi trường cũ
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
