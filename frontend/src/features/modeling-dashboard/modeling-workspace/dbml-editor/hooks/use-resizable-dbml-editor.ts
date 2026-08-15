"use client";

import { useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

export const MIN_DBML_EDITOR_WIDTH_PX = 280;
export const MAX_DBML_EDITOR_WIDTH_PX = 720;
export const DEFAULT_DBML_EDITOR_WIDTH_PX = 420;
export const DBML_EDITOR_KEYBOARD_STEP_PX = 24;

interface ResizeOrigin {
  pointerX: number;
  width: number;
}

/** Quản lý độ rộng DBML editor bằng pointer và bàn phím.
 * @returns Độ rộng hiện tại cùng handlers cho separator.
 * @remarks Pointer capture giữ thao tác resize ổn định khi con trỏ rời separator.
 */
export function useResizableDBMLEditor() {
  const [width, setWidth] = useState(DEFAULT_DBML_EDITOR_WIDTH_PX);
  const originRef = useRef<ResizeOrigin | null>(null);
  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    originRef.current = { pointerX: event.clientX, width };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (!originRef.current) return;
    const nextWidth =
      originRef.current.width + event.clientX - originRef.current.pointerX;
    setWidth(clampEditorWidth(nextWidth));
  };
  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    originRef.current = null;
    event.currentTarget.releasePointerCapture(event.pointerId);
  };
  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    setWidth((current) =>
      clampEditorWidth(current + direction * DBML_EDITOR_KEYBOARD_STEP_PX),
    );
  };
  return {
    width,
    handlePointerDown,
    handlePointerMove,
    handlePointerUp,
    handleKeyDown,
  };
}

function clampEditorWidth(width: number): number {
  return Math.min(
    MAX_DBML_EDITOR_WIDTH_PX,
    Math.max(MIN_DBML_EDITOR_WIDTH_PX, width),
  );
}
