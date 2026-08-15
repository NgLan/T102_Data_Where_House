// @vitest-environment jsdom

import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useWorkspaceShortcuts } from "./use-workspace-shortcuts";

describe("useWorkspaceShortcuts", () => {
  it("gọi lưu và chặn hành vi mặc định khi nhấn Ctrl+S trên draft bẩn", () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() =>
      useWorkspaceShortcuts({
        canSave: true,
        isDirty: true,
        onClearSelection: vi.fn(),
        onSave,
      }),
    );
    const event = new KeyboardEvent("keydown", {
      key: "s",
      ctrlKey: true,
      cancelable: true,
    });
    window.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
    expect(onSave).toHaveBeenCalledOnce();
  });

  it("không gọi lưu khi draft chưa thay đổi", () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() =>
      useWorkspaceShortcuts({
        canSave: true,
        isDirty: false,
        onClearSelection: vi.fn(),
        onSave,
      }),
    );
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "s", ctrlKey: true }));
    expect(onSave).not.toHaveBeenCalled();
  });
});
