"use client";

import {
  RefObject,
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import { parseDbml, serializeDbml } from "@/common/dbml/dbml-adapter";
import type { DbmlDocument } from "@/common/dbml/types";
import {
  dataModelEditorReducer,
  type DataModelAction,
} from "../../model-document/reducers/data-model-editor-reducer";
import { requireParsedDocument } from "../../model-document/utils/data-model-factory";
import { validateDataModel } from "../../model-document/utils/data-model-validation";

/** Đồng bộ DBML source với structured draft mà không chặn trạng thái nhập trung gian.
 * @param initialCode DBML hợp lệ dùng để khởi tạo editor.
 * @returns Document, source code, parse state và các command đồng bộ.
 * @remarks Structured draft chỉ ghi ngược source khi vượt qua validation và exporter.
 */
export function useDocumentSynchronization(initialCode: string) {
  const initialDocument = useMemo(
    () => requireParsedDocument(initialCode),
    [initialCode],
  );
  const [document, dispatchDocument] = useReducer(
    dataModelEditorReducer,
    initialDocument,
  );
  const [code, setCode] = useState(initialCode);
  const [parseError, setParseError] = useState<string | null>(null);
  const documentRef = useRef(document);
  const editVersionRef = useRef(0);
  const synchronizedCodeRef = useRef<string | null>(null);
  useEffect(() => {
    documentRef.current = document;
  }, [document]);
  const actions = useMemo(
    () => ({
      dispatchDocument,
      documentRef,
      editVersionRef,
      synchronizedCodeRef,
      setCode,
      setParseError,
    }),
    [],
  );
  const applyDocument = useApplyDocument(actions);
  useCodeParser(code, actions);
  const mutate = useDocumentMutation(actions);
  const handleChangeCode = useCallback((value: string) => {
    editVersionRef.current += 1;
    setCode(value);
  }, []);
  return {
    document,
    code,
    setCode: handleChangeCode,
    parseError,
    applyDocument,
    mutate,
  };
}

interface SynchronizationActions {
  dispatchDocument: Dispatch<DataModelAction>;
  documentRef: RefObject<DbmlDocument>;
  editVersionRef: RefObject<number>;
  synchronizedCodeRef: RefObject<string | null>;
  setCode: Dispatch<SetStateAction<string>>;
  setParseError: Dispatch<SetStateAction<string | null>>;
}

function useApplyDocument(actions: SynchronizationActions) {
  const {
    dispatchDocument,
    documentRef,
    editVersionRef,
    setCode,
    setParseError,
    synchronizedCodeRef,
  } = actions;
  return useCallback(
    (document: DbmlDocument, code = serializeDbml(document)) => {
      documentRef.current = document;
      editVersionRef.current += 1;
      dispatchDocument({ type: "replace", document });
      synchronizedCodeRef.current = code;
      setCode(code);
      setParseError(null);
    },
    [
      dispatchDocument,
      documentRef,
      editVersionRef,
      setCode,
      setParseError,
      synchronizedCodeRef,
    ],
  );
}

type CodeParserActions = Pick<
  SynchronizationActions,
  | "dispatchDocument"
  | "documentRef"
  | "editVersionRef"
  | "synchronizedCodeRef"
  | "setParseError"
>;

function useCodeParser(code: string, actions: CodeParserActions): void {
  const {
    dispatchDocument,
    documentRef,
    editVersionRef,
    setParseError,
    synchronizedCodeRef,
  } = actions;
  useEffect(() => {
    if (synchronizedCodeRef.current === code) {
      synchronizedCodeRef.current = null;
      return;
    }
    synchronizedCodeRef.current = null;
    const version = editVersionRef.current;
    const timer = window.setTimeout(() => {
      if (version !== editVersionRef.current) return;
      const parsed = parseDbml(code);
      if (!parsed.document) {
        setParseError(parsed.error ?? "INVALID_DBML_CONTENT");
        return;
      }
      setParseError(null);
      documentRef.current = parsed.document;
      dispatchDocument({ type: "replace", document: parsed.document });
    }, 250);
    return () => window.clearTimeout(timer);
  }, [
    code,
    dispatchDocument,
    documentRef,
    editVersionRef,
    setParseError,
    synchronizedCodeRef,
  ]);
}

function useDocumentMutation(options: SynchronizationActions) {
  const {
    dispatchDocument,
    documentRef,
    editVersionRef,
    setCode,
    setParseError,
    synchronizedCodeRef,
  } = options;
  return useCallback(
    (action: DataModelAction) => {
      const next = dataModelEditorReducer(documentRef.current, action);
      documentRef.current = next;
      editVersionRef.current += 1;
      dispatchDocument({ type: "replace", document: next });
      if (Object.keys(validateDataModel(next)).length > 0) {
        setParseError("INVALID_DBML_CONTENT");
        return;
      }
      const nextCode = trySerializeDocument(next);
      if (!nextCode) return setParseError("INVALID_DBML_CONTENT");
      synchronizedCodeRef.current = nextCode;
      setCode(nextCode);
      setParseError(null);
    },
    [
      dispatchDocument,
      documentRef,
      editVersionRef,
      setCode,
      setParseError,
      synchronizedCodeRef,
    ],
  );
}

function trySerializeDocument(document: DbmlDocument): string | null {
  try {
    return serializeDbml(document);
  } catch {
    return null;
  }
}
