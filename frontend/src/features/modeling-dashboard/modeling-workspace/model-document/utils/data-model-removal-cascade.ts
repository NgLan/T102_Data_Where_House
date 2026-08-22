import type { DbmlDocument, DbmlReference } from "../dbml/types";

/** Xóa bảng và mọi relationship phụ thuộc. */
export function removeTableCascade(document: DbmlDocument, tableId: string): DbmlDocument {
  const table = document.tables.find((item) => item.id === tableId);
  if (!table) return document;
  return {
    ...document,
    tables: document.tables.filter((item) => item.id !== tableId),
    references: document.references.filter((reference) => !usesTable(reference, table.schemaName, table.name)),
  };
}

/** Xóa cột và mọi relationship phụ thuộc. */
export function removeColumnCascade(document: DbmlDocument, tableId: string, columnId: string): DbmlDocument {
  const table = document.tables.find((item) => item.id === tableId);
  const column = table?.columns.find((item) => item.id === columnId);
  if (!table || !column) return document;
  return {
    ...document,
    tables: document.tables.map((item) => item.id === tableId ? { ...item, columns: item.columns.filter((entry) => entry.id !== columnId) } : item),
    references: document.references.filter((reference) => !usesColumn(reference, table.schemaName, table.name, column.name)),
  };
}

function usesTable(reference: DbmlReference, schemaName: string, tableName: string): boolean {
  return (reference.fromSchema === schemaName && reference.fromTable === tableName) || (reference.toSchema === schemaName && reference.toTable === tableName);
}

function usesColumn(reference: DbmlReference, schemaName: string, tableName: string, columnName: string): boolean {
  return (reference.fromSchema === schemaName && reference.fromTable === tableName && reference.fromColumns.includes(columnName)) || (reference.toSchema === schemaName && reference.toTable === tableName && reference.toColumns.includes(columnName));
}
