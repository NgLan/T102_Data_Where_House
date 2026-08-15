"use client";

import { useCallback, useMemo, useState } from "react";
import type { DataModelResponse } from "@/api";
import { parseDbml, serializeDbml } from "@/common/dbml/dbml-adapter";
import type { DbmlDocument } from "@/common/dbml/types";
import { useDocumentSynchronization } from "../dbml-editor/hooks/use-document-synchronization";
import { validateDataModel } from "../model-document/utils/data-model-validation";
import { SAMPLE_DBML } from "../model-document/utils/sample-dbml";
import { useDataModelSnapshot } from "./use-data-model-snapshot";
import { useModelingSelection } from "./use-modeling-selection";

/** Quản lý canonical document và điều phối các capability của modeling workspace.
 * @param projectId Định danh project hiện hành hoặc null khi chỉ chỉnh local.
 * @returns State và command cho editor, canvas, inspector và persistence.
 * @remarks DBML draft được giữ nguyên khi generated API trả lỗi hoặc conflict.
 */
export function useModelingWorkspace(projectId: string | null) {
  const synchronization = useDocumentSynchronization(SAMPLE_DBML);
  const snapshotApplication = useSnapshotApplication(
    synchronization.applyDocument,
  );
  const lifecycle = useDataModelSnapshot({
    projectId,
    onSnapshot: snapshotApplication.apply,
  });
  const selection = useModelingSelection(
    synchronization.document,
    synchronization.mutate,
  );
  const validationErrors = useMemo(
    () => validateDataModel(synchronization.document),
    [synchronization.document],
  );
  const isValid = Object.keys(validationErrors).length === 0;
  const save = useWorkspaceSave({
    document: synchronization.document,
    parseError: synchronization.parseError,
    isValid,
    onInvalid: lifecycle.setErrorCode,
    onSave: lifecycle.save,
  });
  return {
    ...synchronization,
    ...selection,
    ...lifecycle,
    validationErrors,
    save,
    isDirty: synchronization.code !== snapshotApplication.originalCode,
    canSave: Boolean(
      projectId &&
        lifecycle.snapshot &&
        lifecycle.status !== "saving" &&
        lifecycle.status !== "conflict" &&
        !synchronization.parseError &&
        isValid,
    ),
  };
}

function useSnapshotApplication(
  applyDocument: (document: DbmlDocument, code?: string) => void,
) {
  const [originalCode, setOriginalCode] = useState(SAMPLE_DBML);
  const apply = useCallback(
    (value: DataModelResponse) => {
      const parsed = parseDbml(value.dbml);
      if (!parsed.document)
        throw new Error(parsed.error ?? "INVALID_DBML_CONTENT");
      setOriginalCode(value.dbml);
      applyDocument(parsed.document, value.dbml);
    },
    [applyDocument],
  );
  return { apply, originalCode };
}

interface WorkspaceSaveOptions {
  document: DbmlDocument;
  parseError: string | null;
  isValid: boolean;
  onInvalid: (code: string) => void;
  onSave: (dbml: string) => Promise<void>;
}

function useWorkspaceSave(options: WorkspaceSaveOptions) {
  return useCallback(async (): Promise<void> => {
    if (options.parseError || !options.isValid) {
      options.onInvalid("INVALID_DBML_CONTENT");
      return;
    }
    await options.onSave(serializeDbml(options.document));
  }, [options]);
}
