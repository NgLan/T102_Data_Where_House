"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  applyNodeChanges,
  type NodeChange,
  type ReactFlowInstance,
} from "@xyflow/react";
import type { DbmlDocument } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelValidationIssueResponse } from "@/api";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";
import {
  loadCanvasLayout,
  reconcileCanvasLayout,
  saveCanvasLayout,
} from "../utils/canvas-layout-storage";
import { mapDocumentToGraph } from "../utils/erd-graph-mapper";
import {
  createStoredLayout,
  synchronizeNodes,
} from "../utils/erd-canvas-state";
import { useERDAutoLayout } from "./use-erd-auto-layout";
import { useERDTableSearch } from "./use-erd-table-search";

interface ERDCanvasOptions {
  document: DbmlDocument;
  projectId: string;
  onSelectTable: (tableId: string | null) => void;
  onSelectReference: (referenceId: string | null) => void;
  validationIssues: DataModelValidationIssueResponse[];
  selectedTableId: string | null;
}

/** Quản lý graph, layout, search và persistence của ERD canvas.
 * @param options Document, project và selection callbacks.
 * @returns React Flow state cùng các event handler ổn định.
 * @remarks Layout được lưu trong localStorage theo project.
 */
export function useERDCanvas(options: ERDCanvasOptions) {
  const tableIds = useMemo(
    () => options.document.tables.map((table) => table.id),
    [options.document.tables],
  );
  const restored = useMemo(
    () => reconcileCanvasLayout(loadCanvasLayout(options.projectId), tableIds),
    [options.projectId, tableIds],
  );
  const graph = useMemo(
    () => mapDocumentToGraph(options.document, restored.positions, options.validationIssues),
    [options.document, options.validationIssues, restored.positions],
  );
  const [nodes, setNodes] = useState<ERDTableNode[]>(graph.nodes);
  const [instance, setInstance] = useState<ReactFlowInstance<
    ERDTableNode,
    ERDRelationshipEdge
  > | null>(null);
  const [query, setQuery] = useState("");
  useEffect(() => {
    if (!instance || !options.selectedTableId) return;
    const node = nodes.find((item) => item.id === options.selectedTableId);
    if (node) void instance.fitView({ nodes: [node], duration: 250, maxZoom: 1.2 });
  }, [instance, nodes, options.selectedTableId]);
  useEffect(
    () => synchronizeNodes(options.document, options.validationIssues, setNodes),
    [options.document, options.validationIssues],
  );
  const persist = useCallback(
    (
      nextNodes: ERDTableNode[],
      viewport = instance?.getViewport() ?? restored.viewport,
    ) => {
      saveCanvasLayout(
        options.projectId,
        createStoredLayout(nextNodes, viewport),
      );
    },
    [instance, options.projectId, restored.viewport],
  );
  const autoLayout = useERDAutoLayout({
    nodes,
    edges: graph.edges,
    instance,
    setNodes,
    persist,
  });
  const findTable = useERDTableSearch({
    nodes,
    query,
    instance,
    onSelectTable: options.onSelectTable,
    onSelectReference: options.onSelectReference,
  });
  const changeNodes = useCallback((changes: NodeChange<ERDTableNode>[]) => {
    setNodes((current) => applyNodeChanges(changes, current));
  }, []);
  return {
    graph,
    nodes,
    instance,
    query,
    setQuery,
    setInstance,
    changeNodes,
    persist,
    autoLayout,
    findTable,
  };
}
