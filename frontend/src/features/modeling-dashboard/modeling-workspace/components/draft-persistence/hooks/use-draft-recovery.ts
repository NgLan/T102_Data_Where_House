"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { DataModelResponse } from "@/api";
import { requestDataModel } from "../../../services/data-model-api";

export interface StoredModelingDraft {
  projectId: string;
  dataModelId: string;
  baseRevision: number;
  dbml: string;
  updatedAt: string;
}

export interface DraftRecoveryCandidate {
  local: StoredModelingDraft;
  server: DataModelResponse;
}

interface DraftRecoveryOptions {
  projectId: string;
  snapshot: DataModelResponse | null;
  dbml: string;
  isDirty: boolean;
  hasConflict: boolean;
  onApplyServer: (snapshot: DataModelResponse) => void;
  onRestoreDbml: (dbml: string) => void;
}

/** Lưu draft local và yêu cầu quyết định trước khi ghi đè revision server. */
export function useDraftRecovery(options: DraftRecoveryOptions) {
  const {
    dbml,
    hasConflict,
    isDirty,
    onApplyServer,
    onRestoreDbml,
    projectId,
    snapshot,
  } = options;
  const [candidate, setCandidate] = useState<DraftRecoveryCandidate | null>(
    null,
  );
  const checkedSnapshot = useRef<string | null>(null);
  const storageKey = `modeling-draft:${projectId}`;

  useEffect(() => {
    if (!snapshot) return;
    const identity = `${snapshot.id}:${snapshot.revision}`;
    if (checkedSnapshot.current === identity) return;
    checkedSnapshot.current = identity;
    const local = readStoredDraft(storageKey);
    if (local && local.dbml !== snapshot.dbml) {
      void Promise.resolve().then(() =>
        setCandidate({ local, server: snapshot }),
      );
    } else if (local) window.localStorage.removeItem(storageKey);
  }, [snapshot, storageKey]);

  useEffect(() => {
    if (!snapshot || candidate) return;
    if (!isDirty) {
      window.localStorage.removeItem(storageKey);
      return;
    }
    const draft: StoredModelingDraft = {
      projectId,
      dataModelId: snapshot.id,
      baseRevision: snapshot.revision,
      dbml,
      updatedAt: new Date().toISOString(),
    };
    window.localStorage.setItem(storageKey, JSON.stringify(draft));
  }, [candidate, dbml, isDirty, projectId, snapshot, storageKey]);

  useEffect(() => {
    if (!hasConflict || !snapshot) return;
    void requestDataModel(projectId).then((server) => {
      const local =
        readStoredDraft(storageKey) ??
        createStoredDraft(projectId, dbml, snapshot);
      setCandidate({ local, server });
    });
  }, [dbml, hasConflict, projectId, snapshot, storageKey]);

  const restore = useCallback(() => {
    if (!candidate) return;
    onApplyServer(candidate.server);
    onRestoreDbml(candidate.local.dbml);
    setCandidate(null);
  }, [candidate, onApplyServer, onRestoreDbml]);
  const discard = useCallback(() => {
    if (!candidate) return;
    onApplyServer(candidate.server);
    window.localStorage.removeItem(storageKey);
    setCandidate(null);
  }, [candidate, onApplyServer, storageKey]);
  return { candidate, restore, discard };
}

function readStoredDraft(key: string): StoredModelingDraft | null {
  try {
    return JSON.parse(
      window.localStorage.getItem(key) ?? "null",
    ) as StoredModelingDraft | null;
  } catch {
    window.localStorage.removeItem(key);
    return null;
  }
}

function createStoredDraft(
  projectId: string,
  dbml: string,
  snapshot: DataModelResponse,
): StoredModelingDraft {
  return {
    projectId,
    dataModelId: snapshot.id,
    baseRevision: snapshot.revision,
    dbml,
    updatedAt: new Date().toISOString(),
  };
}
