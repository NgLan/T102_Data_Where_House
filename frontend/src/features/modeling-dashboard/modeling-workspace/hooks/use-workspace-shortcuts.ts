"use client";

import { useEffect } from "react";

interface WorkspaceShortcutOptions {
  canSave: boolean;
  isDirty: boolean;
  onClearSelection: () => void;
  onSave: () => Promise<void>;
}

/** Đăng ký keyboard shortcuts của modeling workspace.
 * @param options Điều kiện và callbacks cho Escape/Ctrl+S.
 * @returns Không trả dữ liệu.
 * @remarks Đăng ký listener trên window và tự dọn khi dependency đổi.
 */
export function useWorkspaceShortcuts(options: WorkspaceShortcutOptions): void {
  const { canSave, isDirty, onClearSelection, onSave } = options;
  useEffect(() => {
    const handleKeyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClearSelection();
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        if (canSave && isDirty) void onSave();
      }
    };
    window.addEventListener("keydown", handleKeyboard);
    return () => window.removeEventListener("keydown", handleKeyboard);
  }, [canSave, isDirty, onClearSelection, onSave]);
}
