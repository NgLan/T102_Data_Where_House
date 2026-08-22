import type { DbmlDocument, DbmlReference } from "../dbml/types";

interface ColumnRenameInput { tableId: string; columnId: string; name: string }
interface ReferenceColumnRenameInput { schemaName: string; tableName: string; oldName: string; newName: string }

/** Đổi tên bảng và đồng bộ relationship endpoints. */
export function renameTableCascade(document: DbmlDocument, tableId: string, name: string): DbmlDocument {
  const target = document.tables.find((table) => table.id === tableId);
  if (!target) return document;
  return {
    ...document,
    tables: document.tables.map((table) => table.id === tableId ? { ...table, name } : table),
    references: document.references.map((reference) => ({
      ...reference,
      fromTable: reference.fromSchema === target.schemaName && reference.fromTable === target.name ? name : reference.fromTable,
      toTable: reference.toSchema === target.schemaName && reference.toTable === target.name ? name : reference.toTable,
    })),
  };
}

/** Đổi tên cột và đồng bộ composite relationship endpoints. */
export function renameColumnCascade(document: DbmlDocument, input: ColumnRenameInput): DbmlDocument {
  const table = document.tables.find((item) => item.id === input.tableId);
  const column = table?.columns.find((item) => item.id === input.columnId);
  if (!table || !column) return document;
  const renameInput = { schemaName: table.schemaName, tableName: table.name, oldName: column.name, newName: input.name };
  return {
    ...document,
    tables: document.tables.map((item) => item.id === input.tableId ? { ...item, columns: item.columns.map((entry) => entry.id === input.columnId ? { ...entry, name: input.name } : entry) } : item),
    references: document.references.map((reference) => renameReferenceColumn(reference, renameInput)),
  };
}

function renameReferenceColumn(reference: DbmlReference, input: ReferenceColumnRenameInput): DbmlReference {
  const fromColumns = reference.fromSchema === input.schemaName && reference.fromTable === input.tableName ? replaceName(reference.fromColumns, input) : reference.fromColumns;
  const toColumns = reference.toSchema === input.schemaName && reference.toTable === input.tableName ? replaceName(reference.toColumns, input) : reference.toColumns;
  return { ...reference, fromColumns, toColumns, fromColumn: fromColumns[0] ?? "", toColumn: toColumns[0] ?? "" };
}

function replaceName(names: string[], input: ReferenceColumnRenameInput): string[] {
  return names.map((name) => name === input.oldName ? input.newName : name);
}
