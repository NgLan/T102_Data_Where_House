import type { DbmlDocument, DbmlReference } from "@/common/dbml/types";

interface ColumnRenameInput {
  tableId: string;
  columnId: string;
  name: string;
}

interface ReferenceColumnRenameInput {
  schemaName: string;
  tableName: string;
  oldName: string;
  newName: string;
}

/** Đổi tên table và cập nhật mọi relationship endpoint phụ thuộc.
 * @param document Draft hiện hành.
 * @param tableId Định danh table.
 * @param name Tên mới.
 * @returns Draft đã đồng bộ tên table và relationship.
 */
export function renameTableCascade(
  document: DbmlDocument,
  tableId: string,
  name: string,
): DbmlDocument {
  const target = document.tables.find((table) => table.id === tableId);
  if (!target) return document;
  return {
    ...document,
    tables: document.tables.map((table) =>
      table.id === tableId ? { ...table, name } : table,
    ),
    references: document.references.map((reference) => ({
      ...reference,
      fromTable:
        reference.fromSchema === target.schemaName &&
        reference.fromTable === target.name
          ? name
          : reference.fromTable,
      toTable:
        reference.toSchema === target.schemaName &&
        reference.toTable === target.name
          ? name
          : reference.toTable,
    })),
  };
}

/** Đổi tên column và cập nhật composite relationship endpoint phụ thuộc.
 * @param document Draft hiện hành.
 * @param input Định danh table, column và tên mới.
 * @returns Draft đã đồng bộ column và relationship.
 */
export function renameColumnCascade(
  document: DbmlDocument,
  input: ColumnRenameInput,
): DbmlDocument {
  const table = document.tables.find((item) => item.id === input.tableId);
  const column = table?.columns.find((item) => item.id === input.columnId);
  if (!table || !column) return document;
  const renameInput = {
    schemaName: table.schemaName,
    tableName: table.name,
    oldName: column.name,
    newName: input.name,
  };
  const references = document.references.map((reference) =>
    renameReferenceColumn(reference, renameInput),
  );
  return {
    ...document,
    tables: document.tables.map((item) =>
      item.id === input.tableId
        ? {
            ...item,
            columns: item.columns.map((entry) =>
              entry.id === input.columnId
                ? { ...entry, name: input.name }
                : entry,
            ),
          }
        : item,
    ),
    references,
  };
}

/** Xóa table và toàn bộ relationship phụ thuộc.
 * @param document Draft hiện hành.
 * @param tableId Định danh table cần xóa.
 * @returns Draft sau khi cascade.
 */
export function removeTableCascade(
  document: DbmlDocument,
  tableId: string,
): DbmlDocument {
  const table = document.tables.find((item) => item.id === tableId);
  if (!table) return document;
  return {
    ...document,
    tables: document.tables.filter((item) => item.id !== tableId),
    references: document.references.filter(
      (reference) =>
        !(
          reference.fromSchema === table.schemaName &&
          reference.fromTable === table.name
        ) &&
        !(
          reference.toSchema === table.schemaName &&
          reference.toTable === table.name
        ),
    ),
  };
}

/** Xóa column và toàn bộ relationship phụ thuộc.
 * @param document Draft hiện hành.
 * @param tableId Định danh table.
 * @param columnId Định danh column cần xóa.
 * @returns Draft sau khi cascade.
 */
export function removeColumnCascade(
  document: DbmlDocument,
  tableId: string,
  columnId: string,
): DbmlDocument {
  const table = document.tables.find((item) => item.id === tableId);
  const column = table?.columns.find((item) => item.id === columnId);
  if (!table || !column) return document;
  return {
    ...document,
    tables: document.tables.map((item) =>
      item.id === tableId
        ? {
            ...item,
            columns: item.columns.filter((entry) => entry.id !== columnId),
          }
        : item,
    ),
    references: document.references.filter(
      (reference) =>
        !usesColumn(reference, {
          schemaName: table.schemaName,
          tableName: table.name,
          columnName: column.name,
        }),
    ),
  };
}

function renameReferenceColumn(
  reference: DbmlReference,
  input: ReferenceColumnRenameInput,
): DbmlReference {
  const fromColumns =
    reference.fromSchema === input.schemaName &&
    reference.fromTable === input.tableName
      ? reference.fromColumns.map((name) =>
          name === input.oldName ? input.newName : name,
        )
      : reference.fromColumns;
  const toColumns =
    reference.toSchema === input.schemaName &&
    reference.toTable === input.tableName
      ? reference.toColumns.map((name) =>
          name === input.oldName ? input.newName : name,
        )
      : reference.toColumns;
  return {
    ...reference,
    fromColumns,
    toColumns,
    fromColumn: fromColumns[0] ?? "",
    toColumn: toColumns[0] ?? "",
  };
}

interface ColumnEndpoint {
  schemaName: string;
  tableName: string;
  columnName: string;
}

function usesColumn(
  reference: DbmlReference,
  endpoint: ColumnEndpoint,
): boolean {
  return (
    (reference.fromSchema === endpoint.schemaName &&
      reference.fromTable === endpoint.tableName &&
      reference.fromColumns.includes(endpoint.columnName)) ||
    (reference.toSchema === endpoint.schemaName &&
      reference.toTable === endpoint.tableName &&
      reference.toColumns.includes(endpoint.columnName))
  );
}
