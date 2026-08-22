"use client";

import "@xyflow/react/dist/style.css";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import { useSyncExternalStore } from "react";
import type { DataModelValidationIssueResponse } from "@/api";
import type {
  DbmlDocument,
  DbmlReference,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import { useERDCanvas } from "../hooks/use-erd-canvas";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";
import { createReferenceFromConnection } from "../utils/erd-graph-mapper";
import { ERDCanvasToolbar } from "./ERDCanvasToolbar";
import { ERDEmptyState } from "./ERDEmptyState";
import { ERDTableNode as ERDTableNodeComponent } from "./ERDTableNode";

const NODE_TYPES = { "erd-table": ERDTableNodeComponent };
const emptySubscribe = () => () => {};
function useIsMounted() {
  return useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );
}

interface ERDCanvasProps {
  document: DbmlDocument;
  projectId: string;
  selectedTableId: string | null;
  selectedReferenceId: string | null;
  onSelectTable: (tableId: string | null) => void;
  onSelectReference: (referenceId: string | null) => void;
  onCreateReference: (reference: DbmlReference) => void;
  validationIssues?: DataModelValidationIssueResponse[];
}

/** Hiển thị ERD canvas với pan/zoom, drag, minimap, search và ELK layout.
 * @param props Draft DBML và callback selection/mutation.
 * @returns React Flow canvas đồng bộ với canonical document.
 */
export function ERDCanvas(props: ERDCanvasProps) {
  const isMounted = useIsMounted();
  const canvas = useERDCanvas({
    ...props,
    validationIssues: props.validationIssues ?? [],
  });

  const handleConnect = (
    connection: Parameters<typeof createReferenceFromConnection>[1],
  ) => {
    const reference = createReferenceFromConnection(props.document, connection);
    if (reference) props.onCreateReference(reference);
  };

  if (props.document.tables.length === 0) return <ERDEmptyState />;

  return (
    <section className="relative z-0 flex h-full w-full min-h-0 min-w-0 flex-1 flex-col overflow-hidden border-x border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-[#070b14]">
      <ERDCanvasToolbar
        query={canvas.query}
        onChangeQuery={canvas.setQuery}
        onFindTable={canvas.findTable}
        onAutoLayout={() => void canvas.autoLayout()}
      />
      <div className="relative h-full w-full min-h-0 flex-1">
        {isMounted ? (
          <ReactFlow<ERDTableNode, ERDRelationshipEdge>
            nodes={canvas.nodes.map((node) => ({
              ...node,
              selected: node.id === props.selectedTableId,
            }))}
            edges={canvas.graph.edges.map((edge) => ({
              ...edge,
              selected: edge.id === props.selectedReferenceId,
            }))}
            nodeTypes={NODE_TYPES}
            onInit={canvas.setInstance}
            onNodesChange={canvas.changeNodes}
            onNodeDragStop={() => canvas.persist(canvas.nodes)}
            onNodeClick={(_, node) => props.onSelectTable(node.id)}
            onEdgeClick={(_, edge) => props.onSelectReference(edge.id)}
            onPaneClick={() => {
              props.onSelectTable(null);
              props.onSelectReference(null);
            }}
            onConnect={handleConnect}
            onMoveEnd={(_, viewport) => canvas.persist(canvas.nodes, viewport)}
            fitView
            minZoom={0.2}
            maxZoom={2}
            deleteKeyCode={null}
          >
            <Background gap={20} size={1} />
            <Controls />
            <MiniMap pannable zoomable nodeColor="#38bdf8" />
          </ReactFlow>
        ) : (
          <div className="h-full w-full bg-slate-50 dark:bg-[#070b14]" />
        )}
      </div>
    </section>
  );
}
