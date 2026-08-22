"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
} from "react";
import {
  parseDbml,
  serializeDbml,
} from "../../../../model-document/dbml/dbml-adapter";
import type { DbmlDocument } from "../../../../model-document/dbml/types";
import {
  dataModelEditorReducer,
  type DataModelAction,
} from "../../../../model-document/reducers/data-model-editor-reducer";
import { requireParsedDocument } from "../../../../model-document/utils/data-model-factory";
import { validateDataModel } from "../../../../model-document/utils/data-model-validation";

/** Synchronizes DBML source with the structured draft while allowing partial input. */
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
        setParseError(parsed.error ?? "DATA_MODEL_DBML_SYNTAX_INVALID");
        return;
      }
      setParseError(null);
      documentRef.current = parsed.document;
      dispatchDocument({ type: "replace", document: parsed.document });
    }, 250);
    return () => window.clearTimeout(timer);
  }, [code]);

  const applyDocument = useCallback(
    (nextDocument: DbmlDocument, nextCode = serializeDbml(nextDocument)) => {
      documentRef.current = nextDocument;
      editVersionRef.current += 1;
      dispatchDocument({ type: "replace", document: nextDocument });
      synchronizedCodeRef.current = nextCode;
      setCode(nextCode);
      setParseError(null);
    },
    [],
  );

  const mutate = useCallback((action: DataModelAction) => {
    const nextDocument = dataModelEditorReducer(documentRef.current, action);
    documentRef.current = nextDocument;
    editVersionRef.current += 1;
    dispatchDocument({ type: "replace", document: nextDocument });
    if (Object.keys(validateDataModel(nextDocument)).length > 0) {
      setParseError("DATA_MODEL_DBML_SYNTAX_INVALID");
      return;
    }
    try {
      const nextCode = serializeDbml(nextDocument);
      synchronizedCodeRef.current = nextCode;
      setCode(nextCode);
      setParseError(null);
    } catch {
      setParseError("DATA_MODEL_DBML_SYNTAX_INVALID");
    }
  }, []);

  const changeCode = useCallback((value: string) => {
    editVersionRef.current += 1;
    setCode(value);
  }, []);

  return {
    document,
    code,
    setCode: changeCode,
    parseError,
    applyDocument,
    mutate,
  };
}
