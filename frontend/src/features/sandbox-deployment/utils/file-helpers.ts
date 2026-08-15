/**
 * Utilities hỗ trợ tải file về máy người dùng (.sql, .md)
 */

/**
 * Tải file văn bản về trình duyệt
 * @param filename Tên file xuất ra (ví dụ: schema.sql)
 * @param content Nội dung file
 * @param mimeType Loại MIME type
 */
export function downloadTextFile(filename: string, content: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
