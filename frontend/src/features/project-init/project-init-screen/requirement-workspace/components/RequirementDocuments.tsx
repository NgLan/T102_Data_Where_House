"use client";

import { FileText, Trash2, Upload } from "lucide-react";
import { useRef } from "react";
import { useTranslation } from "react-i18next";
import type { RequirementFileResponse } from "@/api";
import { Button } from "@/common/components/ui/button";

interface RequirementDocumentsProps {
  items: RequirementFileResponse[];
  disabled: boolean;
  isLoading: boolean;
  hasError: boolean;
  onUpload: (files: File[]) => void;
  onDelete: (fileId: string) => void;
  onRetry: () => void;
}

/** Compact picker/list; document content stays outside Raw Requirement editor. */
export function RequirementDocuments(props: RequirementDocumentsProps) {
  const { t } = useTranslation("project-init");
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <section className="rounded-lg border bg-muted/20 p-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold">{t("TXT_REQUIREMENT_DOCUMENTS_TITLE")}</h3>
          <p className="text-xs text-muted-foreground">{t("TXT_REQUIREMENT_DOCUMENTS_HELP")}</p>
        </div>
        <Button type="button" size="sm" variant="outline" disabled={props.disabled}
          onClick={() => inputRef.current?.click()}>
          <Upload />
          {t("BTN_UPLOAD_REQUIREMENT_DOCUMENTS")}
        </Button>
        <input ref={inputRef} className="sr-only" type="file" multiple
          disabled={props.disabled} accept=".docx,.txt,.md"
          onChange={(event) => {
            const files = Array.from(event.target.files ?? []);
            if (files.length) props.onUpload(files);
            event.target.value = "";
          }} />
      </div>
      {props.hasError ? (
        <div className="mt-3 flex items-center justify-between rounded-md border border-destructive/30 p-2 text-xs">
          <span>{t("TXT_REQUIREMENT_DOCUMENTS_ERROR")}</span>
          <Button type="button" size="sm" variant="ghost" onClick={props.onRetry}>{t("BTN_RETRY")}</Button>
        </div>
      ) : props.isLoading ? (
        <p className="mt-3 text-xs text-muted-foreground">{t("MSG_LOADING_DOCUMENTS")}</p>
      ) : (
        <div className="mt-3 flex flex-wrap gap-2">
          {props.items.length === 0 && <span className="text-xs text-muted-foreground">{t("TXT_NO_REQUIREMENT_DOCUMENTS")}</span>}
          {props.items.map((item) => (
            <span key={item.id} className="inline-flex items-center gap-1 rounded-full border bg-background px-2.5 py-1 text-xs">
              <FileText className="size-3.5" />
              <span className="max-w-52 truncate">{item.name}</span>
              {!props.disabled && (
                <button type="button" aria-label={t("BTN_DELETE_REQUIREMENT_DOCUMENT")} onClick={() => props.onDelete(item.id)}>
                  <Trash2 className="size-3.5 text-muted-foreground hover:text-destructive" />
                </button>
              )}
            </span>
          ))}
        </div>
      )}
    </section>
  );
}
