/**
 * Utilities hỗ trợ format và copy mã DDL SQL
 */

/**
 * Định dạng cơ bản mã SQL DDL (viết hoa từ khóa chính)
 * @param sql Code DDL thô
 * @returns Code DDL đã định dạng
 */
export function formatSql(sql: string): string {
  if (!sql) return '';
  const keywords = ['CREATE TABLE', 'CREATE SCHEMA', 'PRIMARY KEY', 'REFERENCES', 'NOT NULL', 'INT', 'VARCHAR', 'DECIMAL', 'TIMESTAMP', 'DEFAULT'];
  let formatted = sql;
  keywords.forEach((keyword) => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
    formatted = formatted.replace(regex, keyword);
  });
  return formatted;
}

/**
 * Sao chép văn bản vào hệ thống Clipboard
 * @param text Chuỗi văn bản cần copy
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Không thể sao chép:', err);
    return false;
  }
}
