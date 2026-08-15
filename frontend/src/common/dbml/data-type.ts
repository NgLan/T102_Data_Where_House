import { Parser } from '@dbml/core';

export type DbmlDataTypeParameterKind = 'none' | 'length' | 'precision-scale' | 'precision';

export interface DbmlDataTypePreset {
  value: string;
  aliases: readonly string[];
  parameterKind: DbmlDataTypeParameterKind;
}

export const DBML_DATA_TYPE_PRESETS: readonly DbmlDataTypePreset[] = [
  preset('smallint'), preset('integer', ['int']), preset('bigint'),
  preset('decimal', [], 'precision-scale'), preset('numeric', [], 'precision-scale'),
  preset('real'), preset('float'), preset('double precision', ['double']),
  preset('boolean', ['bool']), preset('char', [], 'length'),
  preset('varchar', [], 'length'), preset('text'), preset('binary', [], 'length'),
  preset('varbinary', [], 'length'), preset('blob'), preset('date'),
  preset('time', [], 'precision'), preset('datetime'),
  preset('timestamp', [], 'precision'), preset('timestamp with time zone', [], 'precision'),
  preset('interval'), preset('uuid'), preset('json'), preset('jsonb'),
];

export const DBML_DATA_TYPES = DBML_DATA_TYPE_PRESETS.map((item) => item.value);

export interface ParsedDbmlDataType {
  baseType: string;
  arguments: string[];
  preset: DbmlDataTypePreset | null;
}

/** Phân tách base type và tham số để editor hiển thị control phù hợp. */
export function parseDbmlDataType(value: string): ParsedDbmlDataType {
  const match = value.trim().match(/^(.*?)(?:\(([^()]*)\))?$/);
  const baseType = stripQuotes(match?.[1].trim() ?? '');
  const argumentsList = match?.[2]?.split(',').map((item) => item.trim()) ?? [];
  return { baseType, arguments: argumentsList, preset: findDataTypePreset(baseType) };
}

/** Kiểm tra data type bằng parser DBML chính thức đang được pin trong dự án. */
export function isValidDbmlDataType(value: string): boolean {
  if (!value.trim()) return false;
  try {
    Parser.parse(`Table __type_test {\n value ${toDbmlTypeLiteral(value)}\n}`, 'dbmlv2');
    return true;
  } catch {
    return false;
  }
}

export function hasValidDbmlTypeParameters(value: string): boolean {
  const parsed = parseDbmlDataType(value);
  const kind = parsed.preset?.parameterKind ?? 'none';
  if (!parsed.arguments.length || kind === 'none') return true;
  if (!parsed.arguments.every((item) => /^\d+$/.test(item))) return false;
  const [first, second] = parsed.arguments.map(Number);
  if (kind === 'length') return parsed.arguments.length === 1 && first > 0;
  if (kind === 'precision') return parsed.arguments.length === 1 && first >= 0;
  return parsed.arguments.length <= 2 && first > 0
    && (second === undefined || second <= first);
}

export function isIntegerDbmlType(value: string): boolean {
  return ['smallint', 'integer', 'bigint'].includes(canonicalBaseType(value));
}

export function canonicalDbmlDataType(value: string): string {
  const parsed = parseDbmlDataType(value);
  const baseType = parsed.preset?.value ?? parsed.baseType.toLowerCase();
  return parsed.arguments.length ? `${baseType}(${parsed.arguments.join(',')})` : baseType;
}

function preset(
  value: string,
  aliases: readonly string[] = [],
  parameterKind: DbmlDataTypeParameterKind = 'none',
): DbmlDataTypePreset {
  return { value, aliases, parameterKind };
}

function findDataTypePreset(baseType: string): DbmlDataTypePreset | null {
  const normalized = baseType.toLowerCase();
  return DBML_DATA_TYPE_PRESETS.find((item) =>
    item.value === normalized || item.aliases.includes(normalized)) ?? null;
}

function canonicalBaseType(value: string): string {
  const parsed = parseDbmlDataType(value);
  return parsed.preset?.value ?? parsed.baseType.toLowerCase();
}

function stripQuotes(value: string): string {
  return value.startsWith('"') && value.endsWith('"') ? value.slice(1, -1) : value;
}

function toDbmlTypeLiteral(value: string): string {
  const trimmed = value.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) return trimmed;
  return /\s/.test(trimmed) ? `"${trimmed.replaceAll('"', '\\"')}"` : trimmed;
}
