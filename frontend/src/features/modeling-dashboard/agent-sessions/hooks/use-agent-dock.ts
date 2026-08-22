"use client";

import { useEffect, useState } from "react";

export type AgentDock = "right" | "inspector-bottom" | "hidden";

/** Lưu vị trí dock Agent theo project. */
export function useAgentDock(projectId: string) {
  const storageKey = `modeling-agent-dock:${projectId}`;
  const [dock, setDock] = useState<AgentDock>("right");
  useEffect(() => {
    const stored = window.localStorage.getItem(storageKey);
    if (stored === "right" || stored === "inspector-bottom" || stored === "hidden") {
      void Promise.resolve().then(() => setDock(stored));
    }
  }, [storageKey]);
  useEffect(() => {
    window.localStorage.setItem(storageKey, dock);
  }, [dock, storageKey]);
  return { dock, setDock };
}
