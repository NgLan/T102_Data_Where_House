import { describe, expect, it } from 'vitest';
import {
  canonicalDbmlDataType,
  DBML_DATA_TYPES,
  hasValidDbmlTypeParameters,
  isIntegerDbmlType,
  isValidDbmlDataType,
  parseDbmlDataType,
} from './data-type';

describe('DBML data type policy', () => {
  it('không chứa preset trùng và chuẩn hóa alias', () => {
    expect(new Set(DBML_DATA_TYPES).size).toBe(DBML_DATA_TYPES.length);
    expect(canonicalDbmlDataType('INT')).toBe('integer');
    expect(canonicalDbmlDataType('bool')).toBe('boolean');
    expect(isIntegerDbmlType('int')).toBe(true);
  });

  it('cho phép custom type đúng cú pháp DBML', () => {
    expect(isValidDbmlDataType('money_domain')).toBe(true);
    expect(isValidDbmlDataType('')).toBe(false);
    expect(parseDbmlDataType('varchar(255)').arguments).toEqual(['255']);
  });

  it.each([
    ['varchar(255)', true],
    ['varchar(0)', false],
    ['varchar(text)', false],
    ['decimal(10,2)', true],
    ['decimal(2,10)', false],
    ['timestamp(0)', true],
  ])('validate tham số số của %s', (dataType, expected) => {
    expect(hasValidDbmlTypeParameters(dataType)).toBe(expected);
  });
});
