"use client";

import { DATA_NODES } from "./constants";
import type { DataNode } from "./types";

/** Hiển thị mạng lưới các điểm nút dữ liệu phát sáng và nhấp nháy đa sắc thái. */
export function TechDataNodes() {
  return (
    <>
      {DATA_NODES.map((node, index) => (
        <DataNodeItem key={index} node={node} />
      ))}
    </>
  );
}

function DataNodeItem({ node }: { node: DataNode }) {
  const animationName = resolveAnimationName(node.animationType);

  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2"
      style={{ top: node.top, left: node.left }}
    >
      <div
        className="rounded-full transition-all"
        style={{
          width: `${node.size}px`,
          height: `${node.size}px`,
          backgroundColor: node.color,
          boxShadow: node.glow,
          animation: `${animationName} ${node.duration} ease-in-out infinite ${node.delay}`,
        }}
      />
      {node.hasRing && (
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border opacity-75"
          style={{
            width: `${node.size * 2.8}px`,
            height: `${node.size * 2.8}px`,
            borderColor: node.color,
            animation: `node-ring 3s cubic-bezier(0, 0, 0.2, 1) infinite ${node.delay}`,
          }}
        />
      )}
    </div>
  );
}

function resolveAnimationName(type: DataNode["animationType"]): string {
  if (type === "twinkle") return "node-twinkle";
  if (type === "ping") return "node-pulse-deep";
  return "node-pulse";
}
