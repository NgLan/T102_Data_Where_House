/**
 * Utility so sánh khác biệt giữa hai đoạn văn bản theo từng dòng (Line Diff).
 *
 * Thuật toán: Longest Common Subsequence (LCS) quy hoạch động — thuần TypeScript,
 * không phụ thuộc thư viện ngoài. Dùng để dựng khung so sánh DBML đề xuất (UC6.1 / FR5.3).
 */

/** Loại thay đổi của một dòng trong kết quả so sánh */
export type DiffLineType = 'added' | 'removed' | 'unchanged';

/** Một dòng trong kết quả so sánh khác biệt */
export interface DiffLine {
  type: DiffLineType;
  text: string;
  /** Số thứ tự dòng ở văn bản gốc (null nếu là dòng được thêm mới) */
  oldLineNo: number | null;
  /** Số thứ tự dòng ở văn bản mới (null nếu là dòng bị xóa) */
  newLineNo: number | null;
}

/** Thống kê số dòng thêm/xóa của một kết quả so sánh */
export interface DiffStats {
  added: number;
  removed: number;
}

/** Giới hạn số dòng để tránh bảng LCS phình quá lớn gây treo trình duyệt */
const MAX_DIFF_LINES = 3000;

/**
 * Tách văn bản thành mảng dòng, chuẩn hóa ký tự xuống dòng của Windows.
 */
function toLines(text: string): string[] {
  if (text === '') return [];
  return text.replace(/\r\n/g, '\n').split('\n');
}

/**
 * Dựng bảng độ dài LCS giữa hai mảng dòng.
 * lcs[i][j] = độ dài chuỗi con chung dài nhất của oldLines[i...] và newLines[j...].
 */
function buildLcsTable(oldLines: string[], newLines: string[]): number[][] {
  const rows = oldLines.length;
  const cols = newLines.length;
  const table: number[][] = Array.from({ length: rows + 1 }, () => new Array<number>(cols + 1).fill(0));

  for (let i = rows - 1; i >= 0; i -= 1) {
    for (let j = cols - 1; j >= 0; j -= 1) {
      table[i][j] =
        oldLines[i] === newLines[j]
          ? table[i + 1][j + 1] + 1
          : Math.max(table[i + 1][j], table[i][j + 1]);
    }
  }
  return table;
}

/**
 * So sánh hai đoạn văn bản và trả về danh sách dòng đã gắn nhãn thêm/xóa/giữ nguyên.
 *
 * @param oldText Nội dung gốc (DBML hiện hành)
 * @param newText Nội dung mới (DBML được đề xuất)
 */
export function diffLines(oldText: string, newText: string): DiffLine[] {
  const oldLines = toLines(oldText);
  const newLines = toLines(newText);

  // Văn bản quá lớn: trả về so sánh thô theo khối để không làm treo giao diện.
  if (oldLines.length > MAX_DIFF_LINES || newLines.length > MAX_DIFF_LINES) {
    return [
      ...oldLines.map((text, index) => buildLine('removed', text, index + 1, null)),
      ...newLines.map((text, index) => buildLine('added', text, null, index + 1)),
    ];
  }

  const table = buildLcsTable(oldLines, newLines);
  const result: DiffLine[] = [];
  let i = 0;
  let j = 0;

  while (i < oldLines.length && j < newLines.length) {
    if (oldLines[i] === newLines[j]) {
      result.push(buildLine('unchanged', oldLines[i], i + 1, j + 1));
      i += 1;
      j += 1;
    } else if (table[i + 1][j] >= table[i][j + 1]) {
      result.push(buildLine('removed', oldLines[i], i + 1, null));
      i += 1;
    } else {
      result.push(buildLine('added', newLines[j], null, j + 1));
      j += 1;
    }
  }

  while (i < oldLines.length) {
    result.push(buildLine('removed', oldLines[i], i + 1, null));
    i += 1;
  }
  while (j < newLines.length) {
    result.push(buildLine('added', newLines[j], null, j + 1));
    j += 1;
  }

  return result;
}

/**
 * Tạo một phần tử DiffLine.
 */
function buildLine(
  type: DiffLineType,
  text: string,
  oldLineNo: number | null,
  newLineNo: number | null
): DiffLine {
  return { type, text, oldLineNo, newLineNo };
}

/**
 * Đếm số dòng được thêm và số dòng bị xóa trong kết quả so sánh.
 */
export function countDiff(lines: DiffLine[]): DiffStats {
  return lines.reduce<DiffStats>(
    (stats, line) => {
      if (line.type === 'added') stats.added += 1;
      if (line.type === 'removed') stats.removed += 1;
      return stats;
    },
    { added: 0, removed: 0 }
  );
}

/**
 * Kiểm tra hai văn bản có thực sự khác nhau hay không.
 */
export function hasChanges(lines: DiffLine[]): boolean {
  return lines.some((line) => line.type !== 'unchanged');
}
