import {
  canonicalDbmlDataType,
  isIntegerDbmlType,
} from "@/common/dbml/data-type";
import { isDbmlDefaultValueCompatible } from "@/common/dbml/default-value";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlReference,
  DbmlTable,
} from "@/common/dbml/types";

export interface EffectiveColumnConstraints {
  isNotNull: boolean;
  isUnique: boolean;
  isCompositePrimaryKey: boolean;
}

export interface DataTypeChangeImpact {
  shouldClearDefault: boolean;
  shouldDisableIncrement: boolean;
  referenceIds: string[];
}

interface DataTypeChangeContext {
  document: DbmlDocument;
  table: DbmlTable;
  column: DbmlColumn;
  nextDataType: string;
}

/** Tính constraint hiệu lực mà không làm mất semantics của composite primary key. */
export function getEffectiveColumnConstraints(
  table: DbmlTable,
  column: DbmlColumn,
): EffectiveColumnConstraints {
  const primaryKeyCount = table.columns.filter(
    (item) => item.isPrimaryKey,
  ).length;
  return {
    isNotNull: column.isPrimaryKey || column.isNotNull,
    isUnique: column.isUnique || (column.isPrimaryKey && primaryKeyCount === 1),
    isCompositePrimaryKey: column.isPrimaryKey && primaryKeyCount > 1,
  };
}

/** Liệt kê dữ liệu phụ thuộc phải dọn khi đổi kiểu cột. */
export function getDataTypeChangeImpact(
  context: DataTypeChangeContext,
): DataTypeChangeImpact {
  const { column, nextDataType } = context;
  return {
    shouldClearDefault: !isDbmlDefaultValueCompatible(
      nextDataType,
      column.defaultValue,
    ),
    shouldDisableIncrement:
      column.isAutoIncrement && !isIntegerDbmlType(nextDataType),
    referenceIds: incompatibleReferences(context),
  };
}

export function getColumnReferences(
  document: DbmlDocument,
  table: DbmlTable,
  column: DbmlColumn,
): DbmlReference[] {
  return document.references.filter(
    (reference) =>
      matchesEndpoint(
        {
          schema: reference.fromSchema,
          table: reference.fromTable,
          columns: reference.fromColumns,
        },
        table,
        column,
      ) ||
      matchesEndpoint(
        {
          schema: reference.toSchema,
          table: reference.toTable,
          columns: reference.toColumns,
        },
        table,
        column,
      ),
  );
}

export function hasDataTypeImpact(impact: DataTypeChangeImpact): boolean {
  return (
    impact.shouldClearDefault ||
    impact.shouldDisableIncrement ||
    impact.referenceIds.length > 0
  );
}

function incompatibleReferences(context: DataTypeChangeContext): string[] {
  const result: string[] = [];
  for (const reference of context.document.references) {
    const counterpart = counterpartColumn({ ...context, reference });
    if (
      counterpart &&
      canonicalDbmlDataType(counterpart.dataType) !==
        canonicalDbmlDataType(context.nextDataType)
    )
      result.push(reference.id);
  }
  return result;
}

interface CounterpartContext extends Omit<
  DataTypeChangeContext,
  "nextDataType"
> {
  reference: DbmlReference;
}

function counterpartColumn(context: CounterpartContext): DbmlColumn | null {
  const { document, reference, table, column } = context;
  const fromIndex =
    reference.fromSchema === table.schemaName &&
    reference.fromTable === table.name
      ? reference.fromColumns.indexOf(column.name)
      : -1;
  const toIndex =
    reference.toSchema === table.schemaName && reference.toTable === table.name
      ? reference.toColumns.indexOf(column.name)
      : -1;
  if (fromIndex >= 0)
    return findColumn(document, {
      schema: reference.toSchema,
      table: reference.toTable,
      column: reference.toColumns[fromIndex],
    });
  if (toIndex >= 0)
    return findColumn(document, {
      schema: reference.fromSchema,
      table: reference.fromTable,
      column: reference.fromColumns[toIndex],
    });
  return null;
}

interface ColumnAddress {
  schema: string;
  table: string;
  column: string;
}

function findColumn(
  document: DbmlDocument,
  address: ColumnAddress,
): DbmlColumn | null {
  return (
    document.tables
      .find(
        (table) =>
          table.schemaName === address.schema && table.name === address.table,
      )
      ?.columns.find((column) => column.name === address.column) ?? null
  );
}

function matchesEndpoint(
  endpoint: { schema: string; table: string; columns: string[] },
  table: DbmlTable,
  column: DbmlColumn,
): boolean {
  return (
    endpoint.schema === table.schemaName &&
    endpoint.table === table.name &&
    endpoint.columns.includes(column.name)
  );
}
