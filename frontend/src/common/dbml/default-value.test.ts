import { describe, expect, it } from 'vitest';
import { getDbmlDefaultEditorKind, isDbmlDefaultValueCompatible } from './default-value';

describe('DBML default value', () => {
  it('phân loại kiểu dữ liệu có precision hoặc length', () => {
    expect(getDbmlDefaultEditorKind('int')).toBe('integer');
    expect(getDbmlDefaultEditorKind('decimal(10,2)')).toBe('decimal');
    expect(getDbmlDefaultEditorKind('boolean')).toBe('boolean');
    expect(getDbmlDefaultEditorKind('varchar(255)')).toBe('text');
  });

  it('chỉ chấp nhận literal tương thích hoặc biểu thức DBML', () => {
    expect(isDbmlDefaultValueCompatible('int', '12')).toBe(true);
    expect(isDbmlDefaultValueCompatible('int', '12.5')).toBe(false);
    expect(isDbmlDefaultValueCompatible('float', '12.5')).toBe(true);
    expect(isDbmlDefaultValueCompatible('boolean', 'true')).toBe(true);
    expect(isDbmlDefaultValueCompatible('boolean', '1')).toBe(false);
    expect(isDbmlDefaultValueCompatible('int', '`nextval()`')).toBe(true);
  });
});
