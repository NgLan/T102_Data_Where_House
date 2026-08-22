"use client";

import { useCallback, useState } from "react";
import type { DbmlDocument, DbmlReference } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelAction } from "../model-document/reducers/data-model-editor-reducer";
import {
  createColumn,
  createTable,
} from "../model-document/utils/data-model-factory";

/** Quản lý selection và command tạo phần tử trong Data Model.
 * @param document Document hiện hành.
 * @param mutate Hàm gửi action vào document reducer.
 * @returns Selection state và các command table, column, relationship.
 */
export function useModelingSelection(
  document: DbmlDocument,
  mutate: (action: DataModelAction) => void,
) {
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);
  const [selectedReferenceId, setSelectedReferenceId] = useState<string | null>(
    null,
  );
  const selectTable = useCallback((tableId: string | null) => {
    setSelectedTableId(tableId);
    if (tableId) setSelectedReferenceId(null);
  }, []);
  const selectReference = useCallback((referenceId: string | null) => {
    setSelectedReferenceId(referenceId);
    if (referenceId) setSelectedTableId(null);
  }, []);
  const addReference = useCallback(
    (reference: DbmlReference) => {
      mutate({ type: "add-reference", reference });
      selectReference(reference.id);
    },
    [mutate, selectReference],
  );
  const addTable = useCallback(() => {
    const table = createTable(document.tables);
    mutate({ type: "add-table", table });
    selectTable(table.id);
  }, [document.tables, mutate, selectTable]);
  const addColumn = useCallback(
    (tableId: string) => {
      const table = document.tables.find((item) => item.id === tableId);
      if (table)
        mutate({
          type: "add-column",
          tableId,
          column: createColumn(table.columns),
        });
    },
    [document.tables, mutate],
  );
  return {
    selectedTableId,
    selectedReferenceId,
    selectTable,
    selectReference,
    setSelectedTableId,
    setSelectedReferenceId,
    addReference,
    addTable,
    addColumn,
  };
}
