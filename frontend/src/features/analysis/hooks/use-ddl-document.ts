"use client";

import { useEffect, useState } from "react";

import { ApiClientError } from "@/api/client";

import { fetchDdl } from "../api/fetch-ddl";
import type { DdlDialect, DdlDocument, DdlRequest } from "../model/ddl-types";

interface DdlState {
  document: DdlDocument | null;
  error: string | null;
  loading: boolean;
}

/** Tải lại DDL khi dialog mở, dialect đổi hoặc người dùng yêu cầu thử lại. */
export function useDdlDocument(
  open: boolean,
  dialect: DdlDialect,
  model: Omit<DdlRequest, "dialect">,
): DdlState & { retry: () => void } {
  const [retryToken, setRetryToken] = useState(0);
  const [state, setState] = useState<DdlState>({
    document: null,
    error: null,
    loading: false,
  });

  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    let active = true;
    queueMicrotask(() => {
      if (active) setState((current) => ({ ...current, error: null, loading: true }));
    });
    fetchDdl({ ...model, dialect }, controller.signal)
      .then((document) => {
        if (active) setState({ document, error: null, loading: false });
      })
      .catch((error: Error) => {
        if (!active || error.name === "AbortError") return;
        const message = error instanceof ApiClientError ? error.message : "Backend chưa sẵn sàng. Vui lòng thử lại.";
        setState({ document: null, error: message, loading: false });
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [dialect, model, open, retryToken]);

  /** Tăng token để thực hiện lại request hiện tại. */
  function retry(): void {
    setRetryToken((token) => token + 1);
  }

  return { ...state, retry };
}
