"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { downloadTextFile } from "@/common/browser/download-text-file";
import { generateDataModelAnalysisDocument } from "../services/data-model-ddl-api";

interface DdlDownloadsInput {
  ddlCode: string;
  projectId: string;
}

/** Tạo command tải SQL và Markdown document từ DDL draft hiện tại. */
export function useDdlDownloads(input: DdlDownloadsInput) {
  const { i18n } = useTranslation("sandbox-deployment");
  const language = i18n?.resolvedLanguage;
  const downloadSql = useCallback(() => downloadTextFile({
    filename: "dwh_schema_ddl.sql",
    content: input.ddlCode,
    mimeType: "text/plain",
  }), [input.ddlCode]);
  const downloadDocument = useCallback(async () => {
    const locale = language?.startsWith("en") ? "en" : "vi";
    const document = await generateDataModelAnalysisDocument(
      input.projectId,
      locale,
    );
    downloadTextFile({
      filename: document.filename,
      content: document.content,
      mimeType: "text/markdown",
    });
  }, [input.projectId, language]);
  return { downloadDocument, downloadSql };
}
