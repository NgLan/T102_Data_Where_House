"use client";

import { useEffect, useRef, useState } from "react";

const AUTOSAVE_DELAY_MS = 5 * 60 * 1_000;
const MAX_RETRY_DELAY_MS = 60_000;

export type AutosaveState = "idle" | "scheduled" | "saving" | "retrying";

interface DraftAutosaveOptions {
  draftKey: string;
  isDirty: boolean;
  canSave: boolean;
  onSave: () => Promise<unknown>;
}

/** Tự lưu sau năm phút ngừng sửa và retry lỗi tạm thời có giới hạn. */
export function useDraftAutosave(options: DraftAutosaveOptions) {
  const { canSave, draftKey, isDirty, onSave } = options;
  const [state, setState] = useState<AutosaveState>("idle");
  const canSaveRef = useRef(canSave);
  useEffect(() => {
    canSaveRef.current = canSave;
  }, [canSave]);

  useEffect(() => {
    if (!isDirty) return;
    void Promise.resolve().then(() => setState("scheduled"));
    let retryCount = 0;
    let timer = window.setTimeout(runSave, AUTOSAVE_DELAY_MS);

    async function runSave(): Promise<void> {
      if (!canSaveRef.current) return;
      setState(retryCount ? "retrying" : "saving");
      const result = await onSave().catch(() => null);
      if (result) {
        setState("idle");
        return;
      }
      retryCount += 1;
      const baseDelay = Math.min(2 ** retryCount * 1_000, MAX_RETRY_DELAY_MS);
      const jitter = Math.round(baseDelay * Math.random() * 0.2);
      timer = window.setTimeout(runSave, baseDelay + jitter);
    }

    return () => window.clearTimeout(timer);
  }, [draftKey, isDirty, onSave]);

  return isDirty ? state : "idle";
}
