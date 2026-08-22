"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

export type CornerPosition =
  | "bottom-right"
  | "bottom-left"
  | "top-left"
  | "top-right";

interface UseCornerDragOptions {
  projectId: string;
  onToggleOpen: () => void;
  onClose: () => void;
}

const DRAG_THRESHOLD_PX = 6;

function subscribe(callback: () => void) {
  window.addEventListener("storage", callback);
  return () => window.removeEventListener("storage", callback);
}

/** Quản lý trạng thái kéo thả di chuyển và tự động snap vào 1 trong 4 góc màn hình. */
export function useCornerDrag({
  projectId,
  onToggleOpen,
  onClose,
}: UseCornerDragOptions) {
  const rootRef = useRef<HTMLDivElement>(null);
  const storageKey = `modeling-validation-position:${projectId}`;

  const [overridePosition, setOverridePosition] =
    useState<CornerPosition | null>(null);

  const storedPosition = useSyncExternalStore(
    subscribe,
    () => {
      if (typeof window === "undefined") return "bottom-right";
      const saved = localStorage.getItem(storageKey) as CornerPosition | null;
      return saved &&
        ["bottom-right", "bottom-left", "top-left", "top-right"].includes(saved)
        ? saved
        : "bottom-right";
    },
    () => "bottom-right",
  );

  const position = overridePosition ?? storedPosition;

  const [dragState, setDragState] = useState<{
    isDragging: boolean;
    startX: number;
    startY: number;
    deltaX: number;
    deltaY: number;
  } | null>(null);

  useEffect(() => {
    const closeOutside = (event: PointerEvent) => {
      if (dragState?.isDragging) return;
      if (!rootRef.current?.contains(event.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("pointerdown", closeOutside);
    return () => document.removeEventListener("pointerdown", closeOutside);
  }, [dragState?.isDragging, onClose]);

  const calculateNearestCorner = (
    clientX: number,
    clientY: number,
  ): CornerPosition => {
    const isLeft = clientX < window.innerWidth / 2;
    const isTop = clientY < window.innerHeight / 2;
    return `${isTop ? "top" : "bottom"}-${isLeft ? "left" : "right"}` as CornerPosition;
  };

  const handlePointerDown = (event: React.PointerEvent) => {
    if (event.button !== 0) return;
    const target = event.currentTarget as HTMLElement;
    target.setPointerCapture(event.pointerId);
    setDragState({
      isDragging: false,
      startX: event.clientX,
      startY: event.clientY,
      deltaX: 0,
      deltaY: 0,
    });
  };

  const handlePointerMove = (event: React.PointerEvent) => {
    if (!dragState) return;
    const deltaX = event.clientX - dragState.startX;
    const deltaY = event.clientY - dragState.startY;
    const isOverThreshold = Math.hypot(deltaX, deltaY) >= DRAG_THRESHOLD_PX;

    setDragState({
      isDragging: dragState.isDragging || isOverThreshold,
      startX: dragState.startX,
      startY: dragState.startY,
      deltaX,
      deltaY,
    });
  };

  const handlePointerUp = (event: React.PointerEvent) => {
    if (!dragState) return;
    const target = event.currentTarget as HTMLElement;
    try {
      target.releasePointerCapture(event.pointerId);
    } catch {
      // ignore
    }

    if (dragState.isDragging) {
      const targetCorner = calculateNearestCorner(event.clientX, event.clientY);
      setOverridePosition(targetCorner);
      localStorage.setItem(storageKey, targetCorner);
    } else {
      onToggleOpen();
    }
    setDragState(null);
  };

  const isDragging = Boolean(dragState?.isDragging);
  const transformStyle =
    dragState?.isDragging && (dragState.deltaX !== 0 || dragState.deltaY !== 0)
      ? `translate3d(${dragState.deltaX}px, ${dragState.deltaY}px, 0)`
      : undefined;

  const transitionStyle = isDragging
    ? "none"
    : "top 0.25s cubic-bezier(0.2, 0.9, 0.3, 1), bottom 0.25s cubic-bezier(0.2, 0.9, 0.3, 1), left 0.25s cubic-bezier(0.2, 0.9, 0.3, 1), right 0.25s cubic-bezier(0.2, 0.9, 0.3, 1), transform 0.25s cubic-bezier(0.2, 0.9, 0.3, 1)";

  return {
    rootRef,
    position,
    isDragging,
    isTop: position.includes("top"),
    isLeft: position.includes("left"),
    dragHandlers: {
      onPointerDown: handlePointerDown,
      onPointerMove: handlePointerMove,
      onPointerUp: handlePointerUp,
    },
    containerStyle: {
      transform: transformStyle,
      transition: transitionStyle,
    },
  };
}
