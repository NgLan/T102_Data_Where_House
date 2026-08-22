"use client";

import { useCallback, useMemo, useState } from "react";
import type { DataModelResponse } from "@/api";
import {
  parseDbml,
  serializeDbml,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/dbml-adapter";
import type { DbmlDocument } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import { useDocumentSynchronization } from "../components/panels/dbml-editor/hooks/use-document-synchronization";
import { validateDataModel } from "../model-document/utils/data-model-validation";
import { EMPTY_DBML } from "../model-document/utils/sample-dbml";
import { useDataModelSnapshot } from "./use-data-model-snapshot";
import { useModelingSelection } from "./use-modeling-selection";

/** Quản lý canonical document và điều phối các capability của modeling workspace.
 * @param projectId Định danh project hiện hành hoặc null khi chỉ chỉnh local.
 * @returns State và command cho editor, canvas, inspector và persistence.
 * @remarks DBML draft được giữ nguyên khi generated API trả lỗi hoặc conflict.
 */
export function useModelingWorkspace(projectId: string | null) {
  const synchronization = useDocumentSynchronization(EMPTY_DBML);
  const snapshotApplication = useSnapshotApplication(
    synchronization.applyDocument,
    synchronization.setCode,
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
    // Lưu thẳng một chuỗi DBML cho trước, không đi qua document đang giữ trong state.
    persist: lifecycle.save,
    // Nạp snapshot Backend vừa trả về (sau khi chấp nhận đề xuất) vào editor và canvas.
    // Dùng `lifecycle.accept` chứ không phải `snapshotApplication.apply`: ngoài việc vẽ
    // lại document, nó còn cập nhật `snapshot` đang giữ id và revision — thiếu bước này
    // thì lần Lưu kế tiếp gửi đi `base_revision` cũ và dính xung đột oan.
    applySnapshot: lifecycle.accept,
    isDirty: synchronization.code !== snapshotApplication.originalCode,
    // Không đòi phải có `snapshot`: dự án chưa có Data Model vẫn lưu được lần đầu.
    canSave: Boolean(
      projectId &&
      synchronization.document.tables.length > 0 &&
      lifecycle.status !== "loading" &&
      lifecycle.status !== "generating" &&
      lifecycle.status !== "saving" &&
      lifecycle.status !== "conflict" &&
      !synchronization.parseError &&
      isValid,
    ),
  };
}

function useSnapshotApplication(
  applyDocument: (document: DbmlDocument, code?: string) => void,
  setCode: (value: string) => void,
) {
  const [originalCode, setOriginalCode] = useState(EMPTY_DBML);
  const apply = useCallback(
    (value: DataModelResponse) => {
      setOriginalCode(value.dbml);
      const parsed = parseDbml(value.dbml);
      if (parsed.document) {
        applyDocument(parsed.document, value.dbml);
        return;
      }
      // Snapshot đã lưu mà canvas không dựng nổi vẫn phải mở ra sửa được: nạp mã thô
      // qua `setCode` để bộ parse của editor chạy và hiện lỗi cú pháp ngay dưới khung
      // soạn thảo. Ném lỗi ở đây thì người dùng chỉ thấy toast đỏ và một workspace trống
      // — không còn đường nào chạm tới mã đang hỏng.
      setCode(value.dbml);
    },
    [applyDocument, setCode],
  );
  return { apply, originalCode };
}

interface WorkspaceSaveOptions {
  document: DbmlDocument;
  parseError: string | null;
  isValid: boolean;
  onInvalid: (code: string) => void;
  onSave: (dbml: string) => Promise<DataModelResponse | null>;
}

function useWorkspaceSave(options: WorkspaceSaveOptions) {
  const { document, isValid, onInvalid, onSave, parseError } = options;
  return useCallback(async (): Promise<DataModelResponse | null> => {
    if (parseError || !isValid) {
      onInvalid("DATA_MODEL_DBML_SYNTAX_INVALID");
      return null;
    }
    return onSave(serializeDbml(document));
  }, [document, isValid, onInvalid, onSave, parseError]);
}
