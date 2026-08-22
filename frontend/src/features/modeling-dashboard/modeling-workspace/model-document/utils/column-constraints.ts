import { isIntegerDbmlType } from "../dbml/data-type";
import { isDbmlDefaultValueCompatible } from "../dbml/default-value";
import type { DbmlColumn, DbmlDocument, DbmlTable } from "../dbml/types";
import { findIncompatibleReferenceIds } from "./column-reference-impact";

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
    referenceIds: findIncompatibleReferenceIds(context),
  };
}

export function hasDataTypeImpact(impact: DataTypeChangeImpact): boolean {
  return (
    impact.shouldClearDefault ||
    impact.shouldDisableIncrement ||
    impact.referenceIds.length > 0
  );
}
