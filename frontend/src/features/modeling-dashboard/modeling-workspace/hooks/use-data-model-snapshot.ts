"use client";

import { useCallback, useEffect } from "react";
import type { DataModelResponse } from "@/api";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import { requestDataModel, requestDataModelUpdate } from "../services/data-model-api";
import type {
  DataModelSnapshotOptions,
  WorkspaceStatus,
} from "../types/modeling-workspace-types";
import { useDataModelSnapshotState } from "./use-data-model-snapshot-state";

/** Quản lý vòng đời tải và lưu snapshot bằng generated SDK.
 * @param options Project hiện tại và callback nhận snapshot hợp lệ.
 * @returns Trạng thái request, normalized error cùng các command tải/lưu.
 * @remarks API error đã được toast toàn cục; conflict vẫn được giữ cho feature xử lý.
 */
export function useDataModelSnapshot(options: DataModelSnapshotOptions) {
  const { notifySuccess } = useAppNotification();
  const state = useDataModelSnapshotState(
    options.onSnapshot,
    Boolean(options.projectId),
  );
  const load = useSnapshotLoader({
    projectId: options.projectId,
    accept: state.accept,
    fail: state.fail,
    setStatus: state.setStatus,
  });
  const save = useSnapshotSaver({
    projectId: options.projectId,
    snapshot: state.snapshot,
    accept: state.accept,
    fail: state.fail,
    onSaved: (revision) =>
      notifySuccess("MSG_DATA_MODEL_SAVED", { params: { revision } }),
    setStatus: state.setStatus,
  });
  useEffect(() => {
    void Promise.resolve().then(load);
  }, [load]);
  return { ...state, load, save };
}

interface SnapshotLoaderOptions {
  projectId: string | null;
  accept: (snapshot: DataModelResponse) => void;
  fail: (error: unknown) => void;
  setStatus: (status: WorkspaceStatus) => void;
}

/** Tạo command tải snapshot và cập nhật lifecycle state. */
function useSnapshotLoader(options: SnapshotLoaderOptions) {
  const { accept, fail, projectId, setStatus } = options;
  return useCallback(async (): Promise<void> => {
    if (!projectId) return;
    setStatus("loading");
    try {
      accept(await requestDataModel(projectId));
    } catch (error: unknown) {
      fail(error);
    }
  }, [accept, fail, projectId, setStatus]);
}

interface SnapshotSaverOptions extends SnapshotLoaderOptions {
  snapshot: DataModelResponse | null;
  onSaved: (revision: number) => void;
}

/** Tạo command lưu DBML và giữ conflict cho workspace xử lý. */
function useSnapshotSaver(options: SnapshotSaverOptions) {
  const { accept, fail, onSaved, projectId, setStatus, snapshot } = options;
  return useCallback(
    async (dbml: string): Promise<void> => {
      if (!projectId || !snapshot) return;
      setStatus("saving");
      try {
        const updated = await requestDataModelUpdate(projectId, snapshot, dbml);
        accept(updated);
        setStatus("saved");
        onSaved(updated.revision);
      } catch (error: unknown) {
        fail(error);
      }
    },
    [accept, fail, onSaved, projectId, setStatus, snapshot],
  );
}
