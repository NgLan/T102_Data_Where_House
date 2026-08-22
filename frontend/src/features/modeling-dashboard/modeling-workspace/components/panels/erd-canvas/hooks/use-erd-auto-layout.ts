"use client";

import { useCallback, type Dispatch, type SetStateAction } from "react";
import type { ReactFlowInstance } from "@xyflow/react";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";
import { calculateErdLayout } from "../utils/erd-layout";

interface ERDAutoLayoutOptions {
  nodes: ERDTableNode[];
  edges: ERDRelationshipEdge[];
  instance: ReactFlowInstance<ERDTableNode, ERDRelationshipEdge> | null;
  setNodes: Dispatch<SetStateAction<ERDTableNode[]>>;
  persist: (nodes: ERDTableNode[]) => void;
}

/** Tạo command bố trí ERD tự động bằng ELK.
 * @param options Graph state, React Flow instance và persistence callback.
 * @returns Command layout bất đồng bộ.
 */
export function useERDAutoLayout(options: ERDAutoLayoutOptions) {
  return useCallback(async (): Promise<void> => {
    const positions = await calculateErdLayout(options.nodes, options.edges);
    const next = options.nodes.map((node) => ({
      ...node,
      position: positions[node.id] ?? node.position,
    }));
    options.setNodes(next);
    options.persist(next);
    window.setTimeout(
      () => void options.instance?.fitView({ padding: 0.15, duration: 300 }),
      0,
    );
  }, [options]);
}
