import { describe, expect, it } from 'vitest';
import { countDiff, diffLines, hasChanges } from './dbml-text-diff';

describe('text-diff', () => {
  it('đánh dấu mọi dòng là không đổi khi hai văn bản giống hệt', () => {
    const diff = diffLines('a\nb\nc', 'a\nb\nc');

    expect(diff.map((line) => line.type)).toEqual(['unchanged', 'unchanged', 'unchanged']);
    expect(hasChanges(diff)).toBe(false);
    expect(countDiff(diff)).toEqual({ added: 0, removed: 0 });
  });

  it('nhận ra dòng được thêm vào giữa văn bản', () => {
    const diff = diffLines('a\nc', 'a\nb\nc');

    expect(diff.map((line) => `${line.type}:${line.text}`)).toEqual([
      'unchanged:a',
      'added:b',
      'unchanged:c',
    ]);
    expect(countDiff(diff)).toEqual({ added: 1, removed: 0 });
  });

  it('nhận ra dòng bị xoá', () => {
    const diff = diffLines('a\nb\nc', 'a\nc');

    expect(diff.map((line) => `${line.type}:${line.text}`)).toEqual([
      'unchanged:a',
      'removed:b',
      'unchanged:c',
    ]);
    expect(countDiff(diff)).toEqual({ added: 0, removed: 1 });
  });

  it('giữ nguyên các dòng chung khi nội dung chỉ dịch vị trí', () => {
    const diff = diffLines('x\na\nb', 'a\nb\ny');

    // Hai dòng `a` và `b` phải được nhận là không đổi thay vì bị đánh dấu xoá rồi thêm lại.
    expect(countDiff(diff)).toEqual({ added: 1, removed: 1 });
    expect(diff.filter((line) => line.type === 'unchanged').map((line) => line.text)).toEqual([
      'a',
      'b',
    ]);
  });

  it('ghi số dòng của bản gốc và bản mới', () => {
    const [first, second] = diffLines('a\nb', 'a\nB');

    expect(first).toMatchObject({ type: 'unchanged', oldLineNo: 1, newLineNo: 1 });
    expect(second.type === 'removed' ? second : { oldLineNo: 2 }).toMatchObject({
      oldLineNo: 2,
    });
  });

  it('coi văn bản rỗng là không có dòng nào', () => {
    expect(diffLines('', '')).toEqual([]);
    expect(diffLines('', 'a')).toEqual([
      { type: 'added', text: 'a', oldLineNo: null, newLineNo: 1 },
    ]);
  });

  it('chuẩn hoá xuống dòng kiểu Windows', () => {
    expect(hasChanges(diffLines('a\r\nb', 'a\nb'))).toBe(false);
  });

  it('xử lý văn bản lớn mà không dựng bảng LCS trong ứng dụng', () => {
    const original = Array.from({ length: 5_000 }, (_, index) => `line-${index}`).join('\n');
    const revised = `${original}\nlast-line`;
    expect(countDiff(diffLines(original, revised))).toEqual({ added: 1, removed: 0 });
  });
});
