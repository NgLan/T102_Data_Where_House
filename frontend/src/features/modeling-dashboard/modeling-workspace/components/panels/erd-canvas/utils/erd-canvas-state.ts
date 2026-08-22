import type { DataModelValidationIssueResponse } from "@/api";
import type { DbmlDocument } from "../../../../model-document/dbml/types";
import type { ERDTableNode } from "../types/erd-canvas-types";
import { mapDocumentToGraph } from "./erd-graph-mapper";
import type { Viewport } from "@xyflow/react";

export function synchronizeNodes(
  document: DbmlDocument,
  validationIssues: DataModelValidationIssueResponse[],
  update: (updater: (nodes: ERDTableNode[]) => ERDTableNode[]) => void,
) {
  const timer = window.setTimeout(() => {
    update(
      (current) =>
        mapDocumentToGraph(
          document,
          Object.fromEntries(current.map((node) => [node.id, node.position])),
          validationIssues,
        ).nodes,
    );
  }, 0);
  return () => window.clearTimeout(timer);
}

export function createStoredLayout(nodes: ERDTableNode[], viewport: Viewport) {
  return {
    version: 1 as const,
    positions: Object.fromEntries(
      nodes.map((node) => [node.id, node.position]),
    ),
    viewport,
  };
}
