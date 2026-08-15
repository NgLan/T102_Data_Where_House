import type { Connection } from "@xyflow/react";
import { canonicalDbmlDataType } from "@/common/dbml/data-type";
import type { DbmlDocument, DbmlReference } from "@/common/dbml/types";
import { getEffectiveColumnConstraints } from "../../model-document/utils/column-constraints";
import { parseColumnHandle } from "./erd-column-handle";

/** Tạo relationship hợp lệ từ thao tác kéo nối hai cột. */
export function createReferenceFromConnection(
  document: DbmlDocument,
  connection: Connection,
): DbmlReference | null {
  const source = parseColumnHandle(connection.sourceHandle);
  const target = parseColumnHandle(connection.targetHandle);
  if (!source || !target) return null;
  const sourceTable = document.tables.find(
    (table) => table.id === source.tableId,
  );
  const targetTable = document.tables.find(
    (table) => table.id === target.tableId,
  );
  const sourceColumn = sourceTable?.columns.find(
    (column) => column.id === source.columnId,
  );
  const targetColumn = targetTable?.columns.find(
    (column) => column.id === target.columnId,
  );
  if (!sourceTable || !targetTable || !sourceColumn || !targetColumn)
    return null;
  if (
    !canCreateReference({
      document,
      sourceTable,
      targetTable,
      sourceColumn,
      targetColumn,
    })
  )
    return null;
  return {
    id: crypto.randomUUID(),
    fromSchema: sourceTable.schemaName,
    fromTable: sourceTable.name,
    fromColumn: sourceColumn.name,
    fromColumns: [sourceColumn.name],
    relation: ">",
    toSchema: targetTable.schemaName,
    toTable: targetTable.name,
    toColumn: targetColumn.name,
    toColumns: [targetColumn.name],
  };
}

interface ReferenceCandidate {
  document: DbmlDocument;
  sourceTable: DbmlDocument["tables"][number];
  targetTable: DbmlDocument["tables"][number];
  sourceColumn: DbmlDocument["tables"][number]["columns"][number];
  targetColumn: DbmlDocument["tables"][number]["columns"][number];
}

function canCreateReference(candidate: ReferenceCandidate): boolean {
  const { document, sourceTable, targetTable, sourceColumn, targetColumn } =
    candidate;
  const target = getEffectiveColumnConstraints(targetTable, targetColumn);
  if (
    !target.isUnique ||
    canonicalDbmlDataType(sourceColumn.dataType) !==
      canonicalDbmlDataType(targetColumn.dataType)
  )
    return false;
  return !document.references.some(
    (reference) =>
      reference.fromSchema === sourceTable.schemaName &&
      reference.fromTable === sourceTable.name &&
      reference.fromColumns.includes(sourceColumn.name) &&
      reference.toSchema === targetTable.schemaName &&
      reference.toTable === targetTable.name &&
      reference.toColumns.includes(targetColumn.name),
  );
}
