"use client";

import { useCallback, useState } from "react";
import type { DataModelResponse } from "@/api";
import type { ApiError } from "@/common/errors/api-error";
import { handleApiError } from "@/common/errors/handle-api-error";
import type { WorkspaceStatus } from "../types/modeling-workspace-types";

/** Quản lý state snapshot và giữ normalized error cho feature-specific handling. */
export function useDataModelSnapshotState(
  onSnapshot: (snapshot: DataModelResponse) => void,
  hasProject: boolean,
) {
  const [snapshot, setSnapshot] = useState<DataModelResponse | null>(null);
  const [status, setStatus] = useState<WorkspaceStatus>(
    hasProject ? "loading" : "ready",
  );
  const [error, setError] = useState<ApiError | null>(null);
  const [localErrorCode, setLocalErrorCode] = useState<string | null>(null);
  const accept = useCallback(
    (value: DataModelResponse) => {
      onSnapshot(value);
      setSnapshot(value);
      setStatus("ready");
      setError(null);
      setLocalErrorCode(null);
    },
    [onSnapshot],
  );
  const fail = useCallback((source: unknown) => {
    const normalized = handleApiError(source);
    setError(normalized);
    setStatus(normalized.kind === "conflict" ? "conflict" : "error");
  }, []);
  const setErrorCode = useCallback(
    (code: string) => setLocalErrorCode(code),
    [],
  );
  return {
    snapshot,
    status,
    error,
    errorCode: localErrorCode ?? error?.errorCode ?? null,
    setStatus,
    setErrorCode,
    accept,
    fail,
  };
}
