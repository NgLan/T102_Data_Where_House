"use client";

import { useCallback } from "react";
import type { ReactFlowInstance } from "@xyflow/react";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";

interface ERDTableSearchOptions {
  nodes: ERDTableNode[];
  query: string;
  instance: ReactFlowInstance<ERDTableNode, ERDRelationshipEdge> | null;
  onSelectTable: (tableId: string | null) => void;
  onSelectReference: (referenceId: string | null) => void;
}

/** Tạo command tìm và focus bảng trên ERD canvas.
 * @param options Query, graph state và selection callbacks.
 * @returns Command tìm kiếm bảng hiện hành.
 */
export function useERDTableSearch(options: ERDTableSearchOptions) {
  return useCallback(() => {
    const query = options.query.trim().toLowerCase();
    const match = options.nodes.find((node) =>
      node.data.table.name.toLowerCase().includes(query),
    );
    if (!match || !options.instance) return;
    options.onSelectTable(match.id);
    options.onSelectReference(null);
    void options.instance.setCenter(
      match.position.x + 130,
      match.position.y + 80,
      {
        zoom: 1.15,
        duration: 300,
      },
    );
  }, [options]);
}
