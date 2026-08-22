import type { DbmlColumn, DbmlDocument, DbmlReference, DbmlTable } from "../dbml/types";

/** Tập mutation hợp lệ đối với canonical Data Model document. */
export type DataModelAction =
  | { type: "replace"; document: DbmlDocument }
  | { type: "add-table"; table: DbmlTable }
  | { type: "update-table"; tableId: string; field: "name" | "note"; value: string }
  | { type: "remove-table"; tableId: string }
  | { type: "add-column"; tableId: string; column: DbmlColumn }
  | { type: "update-column"; tableId: string; columnId: string; field: keyof DbmlColumn; value: string | boolean }
  | { type: "update-column-settings"; tableId: string; columnId: string; patch: Partial<DbmlColumn>; removeReferenceIds?: string[] }
  | { type: "remove-column"; tableId: string; columnId: string }
  | { type: "add-reference"; reference: DbmlReference }
  | { type: "update-reference"; reference: DbmlReference }
  | { type: "remove-reference"; referenceId: string };
