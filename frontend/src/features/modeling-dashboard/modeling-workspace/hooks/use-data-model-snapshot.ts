"use client";

import { useCallback, useEffect } from "react";
import type { DataModelResponse } from "@/api";
import { useAppNotification } from "@/common/notifications";
import { requestDataModel, requestDataModelUpdate } from "../services/data-model-api";
import {
  requestDataModelGeneration,
  requestDataModelRegeneration,
} from "../services/data-model-generation-api";
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
  const generate = useSnapshotGenerator({
    projectId: options.projectId,
    snapshot: state.snapshot,
    accept: state.accept,
    fail: state.fail,
    onGenerated: (revision) =>
      notifySuccess("MSG_DATA_MODEL_GENERATED", { params: { revision } }),
    setStatus: state.setStatus,
  });
  useEffect(() => {
    void Promise.resolve().then(load);
  }, [load]);
  return { ...state, generate, load, save };
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

interface SnapshotGeneratorOptions extends SnapshotLoaderOptions {
  snapshot: DataModelResponse | null;
  onGenerated: (revision: number) => void;
}

/** Tạo initial snapshot hoặc ghi đè snapshot qua workflow tuần tự.
 *
 * Backend đã commit kết quả nên chỉ cần nhận snapshot trả về, không phải lưu thêm.
 */
function useSnapshotGenerator(options: SnapshotGeneratorOptions) {
  const { accept, fail, onGenerated, projectId, setStatus, snapshot } = options;
  return useCallback(async (): Promise<void> => {
    if (!projectId) return;
    setStatus("generating");
    try {
      if (snapshot) {
        const regenerated = await requestDataModelRegeneration(projectId);
        accept(regenerated);
        onGenerated(regenerated.revision);
        return;
      }
      const generated = await requestDataModelGeneration(projectId);
      accept(generated);
      onGenerated(generated.revision);
    } catch (error: unknown) {
      fail(error);
    }
  }, [accept, fail, onGenerated, projectId, setStatus, snapshot]);
}

interface SnapshotSaverOptions extends SnapshotLoaderOptions {
  snapshot: DataModelResponse | null;
  onSaved: (revision: number) => void;
}

/** Lưu trực tiếp DBML và giữ conflict cho workspace xử lý. */
function useSnapshotSaver(options: SnapshotSaverOptions) {
  const { accept, fail, onSaved, projectId, setStatus, snapshot } = options;
  return useCallback(
    async (dbml: string): Promise<DataModelResponse | null> => {
      if (!projectId || !snapshot) return null;
      setStatus("saving");
      try {
        const saved = await requestDataModelUpdate(projectId, snapshot, dbml);
        accept(saved);
        onSaved(saved.revision);
        return saved;
      } catch (error: unknown) {
        fail(error);
        return null;
      }
    },
    [accept, fail, onSaved, projectId, setStatus, snapshot],
  );
}
