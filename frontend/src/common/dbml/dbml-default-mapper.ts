import type { FieldModel, TableModel } from './dbml-library-model';

export function noteValue(note: TableModel['note']): string {
  if (typeof note === 'string') return note;
  return note?.value ?? '';
}

export function formatDefault(value?: FieldModel['dbdefault']): string {
  if (!value) return '';
  if (String(value.value).toLowerCase() === 'null') return 'null';
  if (value.type === 'string') return `'${String(value.value).replaceAll("'", "\\'")}'`;
  if (value.type === 'expression') return `\`${String(value.value)}\``;
  return String(value.value);
}

export function parseDefault(value: string): FieldModel['dbdefault'] | undefined {
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  if (trimmed.toLowerCase() === 'null') return { type: 'boolean', value: 'null' };
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return { type: 'string', value: trimmed.slice(1, -1).replaceAll("\\'", "'") };
  }
  if (trimmed.startsWith('`') && trimmed.endsWith('`')) {
    return { type: 'expression', value: trimmed.slice(1, -1) };
  }
  const numericValue = Number(trimmed);
  if (Number.isFinite(numericValue)) return { type: 'number', value: numericValue };
  if (trimmed === 'true' || trimmed === 'false') {
    return { type: 'boolean', value: trimmed === 'true' };
  }
  return { type: 'expression', value: trimmed };
}
