import type { DbmlColumn, DbmlDocument, DbmlTable } from "../dbml/types";
import { renameColumnCascade } from "../utils/data-model-rename-cascade";
import type { DataModelAction } from "./data-model-actions";

export function updateColumn(document: DbmlDocument, action: Extract<DataModelAction, { type: "update-column" }>): DbmlDocument {
  if (action.field === "name") {
    return renameColumnCascade(document, { tableId: action.tableId, columnId: action.columnId, name: String(action.value) });
  }
  return mapTable(document, action.tableId, (table) => ({
    ...table,
    columns: table.columns.map((column) => column.id === action.columnId ? applyColumnSettings(table, column, { [action.field]: action.value }) : column),
  }));
}

export function updateColumnSettings(document: DbmlDocument, action: Extract<DataModelAction, { type: "update-column-settings" }>): DbmlDocument {
  const updated = mapTable(document, action.tableId, (table) => ({
    ...table,
    columns: table.columns.map((column) => column.id === action.columnId ? applyColumnSettings(table, column, action.patch) : column),
  }));
  const removedIds = new Set(action.removeReferenceIds ?? []);
  return removedIds.size ? { ...updated, references: updated.references.filter((reference) => !removedIds.has(reference.id)) } : updated;
}

export function mapTable(document: DbmlDocument, tableId: string, update: (table: DbmlTable) => DbmlTable): DbmlDocument {
  return { ...document, tables: document.tables.map((table) => table.id === tableId ? update(table) : table) };
}

function applyColumnSettings(table: DbmlTable, column: DbmlColumn, patch: Partial<DbmlColumn>): DbmlColumn {
  if (!column.isPrimaryKey || patch.isPrimaryKey !== false) return { ...column, ...patch };
  const isSinglePrimaryKey = table.columns.filter((item) => item.isPrimaryKey).length === 1;
  return { ...column, ...patch, isNotNull: true, isUnique: isSinglePrimaryKey || column.isUnique };
}
