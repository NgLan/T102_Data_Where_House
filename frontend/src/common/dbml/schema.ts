import { z } from 'zod';
import { hasValidDbmlTypeParameters, isIntegerDbmlType, isValidDbmlDataType } from './data-type';
import { isDbmlDefaultValueCompatible } from './default-value';

const IDENTIFIER_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;

/** Zod schema cho column trong editor. */
export const dbmlColumnSchema = z.object({
  id: z.string().min(1),
  name: z.string().trim().min(1, 'FIELD_REQUIRED').regex(IDENTIFIER_PATTERN, 'INVALID_IDENTIFIER'),
  dataType: z.string().trim()
    .refine(isValidDbmlDataType, 'INVALID_DATA_TYPE')
    .refine(hasValidDbmlTypeParameters, 'INVALID_DATA_TYPE_PARAMETERS'),
  isPrimaryKey: z.boolean(),
  isNotNull: z.boolean(),
  isUnique: z.boolean(),
  isAutoIncrement: z.boolean(),
  defaultValue: z.string().refine(hasBalancedQuotes, 'INVALID_DEFAULT_VALUE'),
  note: z.string(),
  checks: z.array(z.string().trim().min(1, 'INVALID_CHECK_EXPRESSION')),
  extraSettings: z.array(z.string()),
}).superRefine((column, context) => {
  if (!isDbmlDefaultValueCompatible(column.dataType, column.defaultValue)) {
    context.addIssue({ code: 'custom', message: 'INVALID_DEFAULT_FOR_DATA_TYPE', path: ['defaultValue'] });
  }
  if (column.isAutoIncrement && !isIntegerDbmlType(column.dataType)) {
    context.addIssue({ code: 'custom', message: 'INVALID_INCREMENT_DATA_TYPE', path: ['isAutoIncrement'] });
  }
  if (column.isAutoIncrement && column.defaultValue.trim()) {
    context.addIssue({ code: 'custom', message: 'INCREMENT_DEFAULT_CONFLICT', path: ['defaultValue'] });
  }
  if ((column.isNotNull || column.isPrimaryKey)
    && column.defaultValue.trim().toLowerCase() === 'null') {
    context.addIssue({ code: 'custom', message: 'NOT_NULL_DEFAULT_CONFLICT', path: ['defaultValue'] });
  }
});

/** Zod schema cho toàn bộ document và quy tắc unique table/column. */
export const dbmlDocumentSchema = z
  .object({
    preamble: z.string(),
    tables: z.array(
      z.object({
        id: z.string().min(1),
        schemaName: z.string().min(1),
        name: z.string().trim().min(1, 'FIELD_REQUIRED').regex(IDENTIFIER_PATTERN, 'INVALID_IDENTIFIER'),
        note: z.string(),
        columns: z.array(dbmlColumnSchema),
        extraStatements: z.array(z.string()),
      })
    ).min(1, 'TABLE_REQUIRED'),
    references: z.array(
      z.object({
        id: z.string(),
        fromSchema: z.string(),
        fromTable: z.string(),
        fromColumn: z.string(),
        fromColumns: z.array(z.string()),
        relation: z.enum(['>', '<', '-', '<>']),
        toSchema: z.string(),
        toTable: z.string(),
        toColumn: z.string(),
        toColumns: z.array(z.string()),
        name: z.string().optional(),
        onDelete: z.enum(['cascade', 'restrict', 'set null', 'set default', 'no action']).optional(),
        onUpdate: z.enum(['cascade', 'restrict', 'set null', 'set default', 'no action']).optional(),
      })
    ),
    sourceModel: z.unknown(),
  })
  .superRefine((document, context) => {
    addDuplicateIssues(document.tables.map((table) => `${table.schemaName}.${table.name}`),
      ['tables'], context);
    document.tables.forEach((table, tableIndex) => {
      addDuplicateIssues(
        table.columns.map((column) => column.name),
        ['tables', tableIndex, 'columns'],
        context
      );
    });
  });

/** Kiểm tra quote ngoài cùng của DEFAULT không bị lệch. */
function hasBalancedQuotes(value: string): boolean {
  let quote: string | null = null;
  let isEscaped = false;
  for (const character of value) {
    if (isEscaped) isEscaped = false;
    else if (character === '\\') isEscaped = true;
    else if (quote === character) quote = null;
    else if (!quote && (character === "'" || character === '"')) quote = character;
  }
  return quote === null;
}

/** Gắn issue vào các phần tử trùng tên theo cách so sánh không phân biệt hoa thường. */
function addDuplicateIssues(
  names: string[],
  path: Array<string | number>,
  context: z.RefinementCtx
): void {
  const seen = new Map<string, number>();
  names.forEach((name, index) => {
    const normalized = name.trim().toLowerCase();
    if (seen.has(normalized)) {
      context.addIssue({
        code: 'custom',
        message: 'DUPLICATE_IDENTIFIER',
        path: [...path, index, 'name'],
      });
    } else seen.set(normalized, index);
  });
}
