import type { DbmlDocument } from "../dbml/types";
import {
  removeColumnCascade,
  removeTableCascade,
} from "../utils/data-model-removal-cascade";
import { renameTableCascade } from "../utils/data-model-rename-cascade";
import type { DataModelAction } from "./data-model-actions";
import {
  mapTable,
  updateColumn,
  updateColumnSettings,
} from "./data-model-column-reducer";

export type { DataModelAction } from "./data-model-actions";

/** Applies one immutable mutation to the canonical data-model draft. */
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
      return addReference(document, action.reference);
    case "update-reference":
      return updateReference(document, action.reference);
    case "remove-reference":
      return removeReference(document, action.referenceId);
  }
}

function updateTable(
  document: DbmlDocument,
  action: Extract<DataModelAction, { type: "update-table" }>,
): DbmlDocument {
  if (action.field === "name") {
    return renameTableCascade(document, action.tableId, action.value);
  }
  return mapTable(document, action.tableId, (table) => ({
    ...table,
    note: action.value,
  }));
}

function addReference(
  document: DbmlDocument,
  reference: DbmlDocument["references"][number],
): DbmlDocument {
  return { ...document, references: [...document.references, reference] };
}

function updateReference(
  document: DbmlDocument,
  reference: DbmlDocument["references"][number],
): DbmlDocument {
  return {
    ...document,
    references: document.references.map((item) =>
      item.id === reference.id ? reference : item,
    ),
  };
}

function removeReference(
  document: DbmlDocument,
  referenceId: string,
): DbmlDocument {
  return {
    ...document,
    references: document.references.filter((item) => item.id !== referenceId),
  };
}
