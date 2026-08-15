import { describe, expect, it } from 'vitest';
import { resources } from './i18n';

const INTERPOLATION_PATTERN = /{{\s*([A-Za-z][A-Za-z0-9]*)\s*}}/g;
const MODELING_DYNAMIC_KEYS = [
  'BTN_RESIZE_INSPECTOR',
  'COLUMN_BOOLEAN_LABEL',
  'INVALID_DEFAULT_FOR_DATA_TYPE',
  'INVALID_RELATIONSHIP_COLUMNS',
  'INVALID_RELATIONSHIP_ENDPOINT',
  'REFERENTIAL_ACTION_CASCADE',
  'REFERENTIAL_ACTION_RESTRICT',
  'REFERENTIAL_ACTION_SET_NULL',
  'REFERENTIAL_ACTION_SET_DEFAULT',
  'REFERENTIAL_ACTION_NO_ACTION',
] as const;

describe('i18n resources', () => {
  it('giữ parity key và interpolation giữa VI/EN', () => {
    for (const namespace of Object.keys(resources.vi) as Array<keyof typeof resources.vi>) {
      const vi = resources.vi[namespace] as Record<string, string>;
      const en = resources.en[namespace] as Record<string, string>;
      expect(Object.keys(en).sort()).toEqual(Object.keys(vi).sort());
      for (const key of Object.keys(vi)) {
        expect(key).toMatch(/^[A-Z][A-Z0-9_]*$/);
        expect(interpolations(en[key])).toEqual(interpolations(vi[key]));
      }
    }
  });

  it('có đủ key modeling được chọn động tại runtime', () => {
    for (const key of MODELING_DYNAMIC_KEYS) {
      expect(resources.vi['modeling-dashboard'][key]).toBeTruthy();
      expect(resources.en['modeling-dashboard'][key]).toBeTruthy();
    }
  });
});

function interpolations(value: string): string[] {
  return [...value.matchAll(INTERPOLATION_PATTERN)].map((match) => match[1]).sort();
}
