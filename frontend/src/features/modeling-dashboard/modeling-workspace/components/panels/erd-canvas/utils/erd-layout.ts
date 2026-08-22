import ELK from "elkjs/lib/elk.bundled.js";
import type {
  ERDRelationshipEdge,
  ERDTableNode,
} from "../types/erd-canvas-types";

const elk = new ELK();
const NODE_WIDTH = 260;
const NODE_BASE_HEIGHT = 76;
const COLUMN_HEIGHT = 32;

/** Tính layout layered bằng ELK để các bảng không đè lên nhau.
 * @param nodes Node bảng cần bố trí.
 * @param edges Relationship giữa các bảng.
 * @returns Vị trí mới theo định danh node.
 * @throws Error khi ELK không trả về tọa độ hợp lệ.
 */
export async function calculateErdLayout(
  nodes: ERDTableNode[],
  edges: ERDRelationshipEdge[],
): Promise<Record<string, { x: number; y: number }>> {
  const graph = await elk.layout({
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "RIGHT",
      "elk.spacing.nodeNode": "60",
      "elk.layered.spacing.nodeNodeBetweenLayers": "100",
    },
    children: nodes.map((node) => ({
      id: node.id,
      width: NODE_WIDTH,
      height: NODE_BASE_HEIGHT + node.data.table.columns.length * COLUMN_HEIGHT,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })),
  });
  return Object.fromEntries(
    (graph.children ?? []).map((node) => {
      if (node.x === undefined || node.y === undefined)
        throw new Error("ELK_LAYOUT_MISSING_POSITION");
      return [node.id, { x: node.x, y: node.y }];
    }),
  );
}
