import type { DbmlDocument, DbmlReference, DbmlTable } from "@/common/dbml/types";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";
import { createColumnHandle } from "./erd-column-handle";

export const DEFAULT_NODE_POSITION = { x: 40, y: 40 };

export { createColumnHandle } from "./erd-column-handle";
export { createReferenceFromConnection } from "./erd-reference-factory";

/** Chuyển document DBML thành node và edge dùng trực tiếp bởi React Flow. */
export function mapDocumentToGraph(
  document: DbmlDocument,
  positions: Record<string, { x: number; y: number }>,
): { nodes: ERDTableNode[]; edges: ERDRelationshipEdge[] } {
  return {
    nodes: document.tables.map<ERDTableNode>((table, index) => ({
      id: table.id,
      type: "erd-table",
      position: positions[table.id] ?? defaultPosition(index),
      data: {
        table,
        foreignKeyColumnIds: getForeignKeyColumnIds(document, table),
      },
    })),
    edges: document.references.flatMap((reference) => {
      const edge = mapReferenceToEdge(document, reference);
      return edge ? [edge] : [];
    }),
  };
}

function mapReferenceToEdge(
  document: DbmlDocument,
  reference: DbmlReference,
): ERDRelationshipEdge | null {
  const source = document.tables.find(
    (table) =>
      table.schemaName === reference.fromSchema &&
      table.name === reference.fromTable,
  );
  const target = document.tables.find(
    (table) =>
      table.schemaName === reference.toSchema &&
      table.name === reference.toTable,
  );
  const sourceColumn = source?.columns.find(
    (column) => column.name === reference.fromColumn,
  );
  const targetColumn = target?.columns.find(
    (column) => column.name === reference.toColumn,
  );
  if (!source || !target || !sourceColumn || !targetColumn) return null;
  return {
    id: reference.id,
    source: source.id,
    target: target.id,
    sourceHandle: createColumnHandle(source.id, sourceColumn.id, "source"),
    targetHandle: createColumnHandle(target.id, targetColumn.id, "target"),
    label: relationshipLabel(reference.relation),
    data: { reference },
    type: "smoothstep",
  };
}

function defaultPosition(index: number): { x: number; y: number } {
  return { x: 40 + (index % 3) * 280, y: 40 + Math.floor(index / 3) * 260 };
}

function relationshipLabel(relation: DbmlReference["relation"]): string {
  if (relation === "-") return "1 : 1";
  if (relation === "<") return "1 : N";
  return relation === "<>" ? "N : N" : "N : 1";
}

function getForeignKeyColumnIds(
  document: DbmlDocument,
  table: DbmlTable,
): string[] {
  const fkColumnNames = new Set<string>();
  for (const reference of document.references) {
    if (
      reference.fromSchema === table.schemaName &&
      reference.fromTable === table.name
    ) {
      if (reference.fromColumn) fkColumnNames.add(reference.fromColumn);
      reference.fromColumns?.forEach((col) => fkColumnNames.add(col));
    }
    if (
      reference.toSchema === table.schemaName &&
      reference.toTable === table.name
    ) {
      if (reference.toColumn) fkColumnNames.add(reference.toColumn);
      reference.toColumns?.forEach((col) => fkColumnNames.add(col));
    }
  }
  return table.columns
    .filter((col) => fkColumnNames.has(col.name))
    .map((col) => col.id);
}
