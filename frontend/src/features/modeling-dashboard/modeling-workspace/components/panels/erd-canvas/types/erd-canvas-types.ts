import type { Edge, Node, Viewport } from "@xyflow/react";
import type { DbmlReference, DbmlTable } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelValidationIssueResponse } from "@/api";

/** Dữ liệu gắn với một React Flow table node. */
export interface ERDTableNodeData extends Record<string, unknown> {
  table: DbmlTable;
  foreignKeyColumnIds?: string[];
  validationIssues?: DataModelValidationIssueResponse[];
}

/** React Flow node đại diện cho bảng DBML. */
export type ERDTableNode = Node<ERDTableNodeData, "erd-table">;
/** React Flow edge đại diện cho relationship DBML. */
export type ERDRelationshipEdge = Edge<{ reference: DbmlReference }>;

/** Layout ERD được lưu theo project trong localStorage. */
export interface StoredCanvasLayout {
  version: 1;
  positions: Record<string, { x: number; y: number }>;
  viewport: Viewport;
}
