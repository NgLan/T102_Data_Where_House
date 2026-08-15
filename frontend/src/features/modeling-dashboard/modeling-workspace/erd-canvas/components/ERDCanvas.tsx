"use client";

import "@xyflow/react/dist/style.css";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import { LocateFixed, Network, Search } from "lucide-react";
import { useSyncExternalStore } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import type { DbmlDocument, DbmlReference } from "@/common/dbml/types";
import { useERDCanvas } from "../hooks/use-erd-canvas";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";
import { createReferenceFromConnection } from "../utils/erd-graph-mapper";
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
}

/** Hiển thị ERD canvas với pan/zoom, drag, minimap, search và ELK layout.
 * @param props Draft DBML và callback selection/mutation.
 * @returns React Flow canvas đồng bộ với canonical document.
 */
export function ERDCanvas(props: ERDCanvasProps) {
  const { t } = useTranslation("modeling-dashboard");
  const isMounted = useIsMounted();
  const canvas = useERDCanvas(props);
  const handleConnect = (
    connection: Parameters<typeof createReferenceFromConnection>[1],
  ) => {
    const reference = createReferenceFromConnection(props.document, connection);
    if (reference) props.onCreateReference(reference);
  };
  if (props.document.tables.length === 0) return <ERDEmptyState />;
  return (
    <section className="relative z-0 flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden border-x border-slate-200 bg-slate-50">
      <div className="flex items-center gap-2 border-b bg-white px-3 py-2">
        <Network className="size-4 shrink-0 text-blue-600" aria-hidden="true" />
        <strong className="shrink-0 text-xs text-slate-700 whitespace-nowrap">
          {t("TXT_CANVAS_TITLE")}
        </strong>
        <div className="flex flex-1 items-center gap-1 min-w-0">
          <Input
            value={canvas.query}
            onChange={(event) => canvas.setQuery(event.target.value)}
            onKeyDown={(event) => event.key === "Enter" && canvas.findTable()}
            placeholder={t("TABLE_SEARCH_PLACEHOLDER")}
            className="h-7 flex-1 min-w-0"
          />
          <Button
            type="button"
            size="icon-sm"
            variant="outline"
            onClick={canvas.findTable}
            aria-label={t("BTN_FIND_TABLE")}
            className="shrink-0"
          >
            <Search />
          </Button>
        </div>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() => void canvas.autoLayout()}
          className="shrink-0 whitespace-nowrap"
        >
          <LocateFixed />
          {t("BTN_AUTO_LAYOUT")}
        </Button>
      </div>
      <div className="min-h-0 flex-1">
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
            <MiniMap pannable zoomable nodeColor="#334155" />
          </ReactFlow>
        ) : (
          <div className="h-full w-full bg-slate-50" />
        )}
      </div>
    </section>
  );
}

function ERDEmptyState() {
  const { t } = useTranslation("modeling-dashboard");
  return (
    <section className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 border-x bg-slate-50 p-8 text-center">
      <Network className="size-12 text-slate-300" />
      <strong>{t("TXT_EMPTY_MODEL_TITLE")}</strong>
      <p className="max-w-sm text-sm text-slate-500">
        {t("TXT_EMPTY_MODEL_DESCRIPTION")}
      </p>
    </section>
  );
}
