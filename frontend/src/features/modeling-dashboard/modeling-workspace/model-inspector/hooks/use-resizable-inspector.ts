"use client";

import { useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

export const MIN_INSPECTOR_WIDTH_PX = 400;
export const MAX_INSPECTOR_WIDTH_PX = 960;
export const DEFAULT_INSPECTOR_WIDTH_PX = 600;
export const INSPECTOR_KEYBOARD_STEP_PX = 24;

interface ResizeOrigin {
  pointerX: number;
  width: number;
}

/** Quản lý độ rộng inspector từ cạnh trái bằng pointer hoặc bàn phím.
 * @returns Độ rộng hiện tại và các event handler của separator.
 * @remarks Kéo sang trái làm inspector rộng hơn; pointer capture giữ thao tác liên tục.
 */
export function useResizableInspector() {
  const [width, setWidth] = useState(DEFAULT_INSPECTOR_WIDTH_PX);
  const originRef = useRef<ResizeOrigin | null>(null);
  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    originRef.current = { pointerX: event.clientX, width };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (!originRef.current) return;
    const pointerDelta = event.clientX - originRef.current.pointerX;
    setWidth(clampInspectorWidth(originRef.current.width - pointerDelta));
  };
  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    originRef.current = null;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };
  const handlePointerCancel = () => {
    originRef.current = null;
  };
  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const direction = event.key === "ArrowLeft" ? 1 : -1;
    setWidth((current) =>
      clampInspectorWidth(current + direction * INSPECTOR_KEYBOARD_STEP_PX),
    );
  };
  return {
    width,
    handlePointerDown,
    handlePointerMove,
    handlePointerUp,
    handlePointerCancel,
    handleKeyDown,
  };
}

function clampInspectorWidth(width: number): number {
  return Math.min(
    MAX_INSPECTOR_WIDTH_PX,
    Math.max(MIN_INSPECTOR_WIDTH_PX, width),
  );
}
