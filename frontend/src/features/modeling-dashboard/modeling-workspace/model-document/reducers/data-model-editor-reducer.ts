import type {
  DbmlColumn,
  DbmlDocument,
  DbmlReference,
  DbmlTable,
} from "@/common/dbml/types";
import {
  removeColumnCascade,
  removeTableCascade,
  renameColumnCascade,
  renameTableCascade,
} from "../utils/data-model-cascade";

/** Tập mutation hợp lệ đối với canonical Data Model document. */
export type DataModelAction =
  | { type: "replace"; document: DbmlDocument }
  | { type: "add-table"; table: DbmlTable }
  | {
      type: "update-table";
      tableId: string;
      field: "name" | "note";
      value: string;
    }
  | { type: "remove-table"; tableId: string }
  | { type: "add-column"; tableId: string; column: DbmlColumn }
  | {
      type: "update-column";
      tableId: string;
      columnId: string;
      field: keyof DbmlColumn;
      value: string | boolean;
    }
  | {
      type: "update-column-settings";
      tableId: string;
      columnId: string;
      patch: Partial<DbmlColumn>;
      removeReferenceIds?: string[];
    }
  | { type: "remove-column"; tableId: string; columnId: string }
  | { type: "add-reference"; reference: DbmlReference }
  | { type: "update-reference"; reference: DbmlReference }
  | { type: "remove-reference"; referenceId: string };

/**
 * Áp dụng một mutation thuần lên Data Model draft.
 *
 * @param document Document hiện tại.
 * @param action Mutation cần thực thi.
 * @returns Document mới không dùng chung collection đã thay đổi.
 */
export function dataModelEditorReducer(
  document: DbmlDocument,
  action: DataModelAction,
): DbmlDocument {
  switch (action.type) {
    case "replace":
      return action.document;
    case "add-table":
      return { ...document, tables: [...document.tables, action.table] };
    case "update-table":
      return updateTable(document, action);
    case "remove-table":
      return removeTableCascade(document, action.tableId);
    case "add-column":
      return mapTable(document, action.tableId, (table) => ({
        ...table,
        columns: [...table.columns, action.column],
      }));
    case "update-column":
      return updateColumn(document, action);
    case "update-column-settings":
      return updateColumnSettings(document, action);
    case "remove-column":
      return removeColumnCascade(document, action.tableId, action.columnId);
    case "add-reference":
      return {
        ...document,
        references: [...document.references, action.reference],
      };
    case "update-reference":
      return {
        ...document,
        references: document.references.map((item) =>
          item.id === action.reference.id ? action.reference : item,
        ),
      };
    case "remove-reference":
      return {
        ...document,
        references: document.references.filter(
          (item) => item.id !== action.referenceId,
        ),
      };
  }
}

function updateTable(
  document: DbmlDocument,
  action: Extract<DataModelAction, { type: "update-table" }>,
): DbmlDocument {
  if (action.field === "name")
    return renameTableCascade(document, action.tableId, action.value);
  return mapTable(document, action.tableId, (table) => ({
    ...table,
    note: action.value,
  }));
}

function updateColumn(
  document: DbmlDocument,
  action: Extract<DataModelAction, { type: "update-column" }>,
): DbmlDocument {
  if (action.field === "name")
    return renameColumnCascade(document, {
      tableId: action.tableId,
      columnId: action.columnId,
      name: String(action.value),
    });
  return mapTable(document, action.tableId, (item) => ({
    ...item,
    columns: item.columns.map((entry) =>
      entry.id === action.columnId
        ? updateColumnField({
            table: item,
            column: entry,
            field: action.field,
            value: action.value,
          })
        : entry,
    ),
  }));
}

interface ColumnFieldUpdate {
  table: DbmlTable;
  column: DbmlColumn;
  field: keyof DbmlColumn;
  value: string | boolean;
}

function updateColumnField(input: ColumnFieldUpdate): DbmlColumn {
  const { table, column, field, value } = input;
  return applyColumnSettings(table, column, { [field]: value });
}

function updateColumnSettings(
  document: DbmlDocument,
  action: Extract<DataModelAction, { type: "update-column-settings" }>,
): DbmlDocument {
  const updated = mapTable(document, action.tableId, (table) => ({
    ...table,
    columns: table.columns.map((column) =>
      column.id === action.columnId
        ? applyColumnSettings(table, column, action.patch)
        : column,
    ),
  }));
  const removedIds = new Set(action.removeReferenceIds ?? []);
  return removedIds.size
    ? {
        ...updated,
        references: updated.references.filter(
          (reference) => !removedIds.has(reference.id),
        ),
      }
    : updated;
}

function applyColumnSettings(
  table: DbmlTable,
  column: DbmlColumn,
  patch: Partial<DbmlColumn>,
): DbmlColumn {
  if (!column.isPrimaryKey || patch.isPrimaryKey !== false)
    return { ...column, ...patch };
  const isSinglePrimaryKey =
    table.columns.filter((item) => item.isPrimaryKey).length === 1;
  return {
    ...column,
    ...patch,
    isNotNull: true,
    isUnique: isSinglePrimaryKey || column.isUnique,
  };
}

function mapTable(
  document: DbmlDocument,
  tableId: string,
  update: (table: DbmlTable) => DbmlTable,
): DbmlDocument {
  return {
    ...document,
    tables: document.tables.map((table) =>
      table.id === tableId ? update(table) : table,
    ),
  };
}
