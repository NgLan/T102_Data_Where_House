import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resources } from './i18n';

const INTERPOLATION_PATTERN = /{{\s*([A-Za-z][A-Za-z0-9]*)\s*}}/g;
const MODELING_DYNAMIC_KEYS = [
  'BTN_RESIZE_INSPECTOR',
  'MSG_INVALID_DEFAULT_FOR_DATA_TYPE',
  'MSG_INVALID_RELATIONSHIP_COLUMNS',
  'MSG_INVALID_RELATIONSHIP_ENDPOINT',
  'TXT_REFERENTIAL_ACTION_CASCADE',
  'TXT_REFERENTIAL_ACTION_RESTRICT',
  'TXT_REFERENTIAL_ACTION_SET_NULL',
  'TXT_REFERENTIAL_ACTION_SET_DEFAULT',
  'TXT_REFERENTIAL_ACTION_NO_ACTION',
] as const;

describe('i18n resources', () => {
  it('giữ parity key và interpolation giữa VI/EN', () => {
    for (const namespace of Object.keys(resources.vi) as Array<keyof typeof resources.vi>) {
      const vi = resources.vi[namespace] as Record<string, string>;
      const en = resources.en[namespace] as Record<string, string>;
      expect(Object.keys(en).sort()).toEqual(Object.keys(vi).sort());
      for (const key of Object.keys(vi)) {
        expect(key).toMatch(/^[A-Z][A-Z0-9_]*$/);
        if (namespace !== 'errors') {
          expect(key).toMatch(/^(?:BTN_|TXT_|MSG_).+|.+_(?:LABEL|PLACEHOLDER)$/);
        }
        expect(typeof vi[key]).toBe('string');
        expect(interpolations(en[key])).toEqual(interpolations(vi[key]));
      }
    }
  });

  it('có đủ key modeling được chọn động tại runtime', () => {
    for (const key of MODELING_DYNAMIC_KEYS) {
      expect(resources.vi['model-inspector'][key]).toBeTruthy();
      expect(resources.en['model-inspector'][key]).toBeTruthy();
    }
  });

  it('đăng ký đầy đủ namespace modeling đã tách theo consumer', () => {
    for (const namespace of [
      'modeling-dashboard', 'modeling-workspace', 'model-inspector',
      'ai-insights', 'ai-chat', 'proposal-review',
    ] as const) {
      expect(resources.vi[namespace]).toBeDefined();
      expect(resources.en[namespace]).toBeDefined();
    }
  });

  it('dịch đầy đủ mọi Backend ErrorCode cho cả VI và EN', () => {
    const source = readFileSync('../backend/src/common/exceptions/error_codes.py', 'utf8');
    const codes = [...source.matchAll(/^\s+([A-Z][A-Z0-9_]+)\s*=\s*"/gm)]
      .map((match) => match[1]);
    for (const code of codes) {
      expect(resources.vi.errors).toHaveProperty(code);
      expect(resources.en.errors).toHaveProperty(code);
    }
  });
});

function interpolations(value: string): string[] {
  return [...value.matchAll(INTERPOLATION_PATTERN)].map((match) => match[1]).sort();
}
