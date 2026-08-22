"use client";

import { useCallback } from "react";
import { copyTextToClipboard } from "@/common/browser/copy-text-to-clipboard";
import { useAppNotification } from "@/common/notifications";
import type { DdlDialect } from "../../../constants/supported-ddl-dialects";
import { formatDdl } from "../utils/format-ddl";
import { useDdlDownloads } from "./use-ddl-downloads";

interface DdlEditorActionsInput {
  ddlCode: string;
  dialect: DdlDialect;
  databaseName: string;
  onDdlCodeChange: (value: string) => void;
}

/** Tạo các command local của DDL editor, không sở hữu server state. */
export function useDdlEditorActions(input: DdlEditorActionsInput) {
  const { notifySuccess, notifyWarning } = useAppNotification();
  const downloads = useDdlDownloads(input);
  const format = useCallback(() => {
    try {
      input.onDdlCodeChange(formatDdl(input.ddlCode, input.dialect));
    } catch {
      notifyWarning("MSG_DDL_FORMAT_FAILED");
    }
  }, [input, notifyWarning]);
  const copy = useCallback(async () => {
    if (await copyTextToClipboard(input.ddlCode)) {
      notifySuccess("MSG_DDL_COPIED");
      return;
    }
    notifyWarning("MSG_CLIPBOARD_UNAVAILABLE");
  }, [input.ddlCode, notifySuccess, notifyWarning]);
  return { copy, format, ...downloads };
}
