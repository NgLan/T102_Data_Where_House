"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { buildDdlDocument } from "../utils/build-ddl-document";
import { downloadTextFile } from "../utils/download-text-file";

interface DdlDownloadsInput {
  ddlCode: string;
  databaseName: string;
}

/** Tạo command tải SQL và Markdown document từ DDL draft hiện tại. */
export function useDdlDownloads(input: DdlDownloadsInput) {
  const { t } = useTranslation("sandbox-deployment");
  const downloadSql = useCallback(() => downloadTextFile({
    filename: "dwh_schema_ddl.sql",
    content: input.ddlCode,
    mimeType: "text/plain",
  }), [input.ddlCode]);
  const downloadDocument = useCallback(() => downloadTextFile({
    filename: "schema_documentation.md",
    content: buildDdlDocument({
      title: t("TXT_DOCUMENT_TITLE"),
      databaseName: input.databaseName,
      ddlCode: input.ddlCode,
    }),
    mimeType: "text/markdown",
  }), [input.databaseName, input.ddlCode, t]);
  return { downloadDocument, downloadSql };
}
