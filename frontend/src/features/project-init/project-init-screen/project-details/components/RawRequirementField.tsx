"use client";

import { useState } from "react";
import { Controller, type Control } from "react-hook-form";
import { FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTranslation } from "react-i18next";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { FileDropzone } from "@/common/components/files/FileDropzone";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/common/components/ui/tabs";
import { Textarea } from "@/common/components/ui/textarea";
import type { ProjectDetailsValues } from "../schemas/project-details-schema";
import { parseRequirementDocument } from "../services/requirement-document-parser";

const DOCUMENT_ACCEPT = {
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/markdown": [".md"],
  "text/plain": [".txt"],
};

interface RawRequirementFieldProps {
  control: Control<ProjectDetailsValues>;
  disabled: boolean;
  error?: string;
}

/** Cho phép soạn Markdown hoặc nhập nội dung từ DOCX/TXT/MD rồi xem trước an toàn. */
export function RawRequirementField(props: RawRequirementFieldProps) {
  const { t } = useTranslation("project-init");
  const [tab, setTab] = useState("edit");
  const [importError, setImportError] = useState(false);
  return (
    <Controller name="requirement" control={props.control} render={({ field }) => (
      <Field data-invalid={Boolean(props.error || importError)}>
        <FieldLabel htmlFor="project-requirement">{t("REQUIREMENT_LABEL")}</FieldLabel>
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="edit">{t("TXT_REQUIREMENT_EDIT_TAB")}</TabsTrigger>
            <TabsTrigger value="preview">{t("TXT_REQUIREMENT_PREVIEW_TAB")}</TabsTrigger>
          </TabsList>
          <TabsContent value="edit">
            <Textarea id="project-requirement" className="min-h-64 resize-y"
              disabled={props.disabled} value={field.value} onChange={field.onChange}
              placeholder={t("REQUIREMENT_OPTIONAL_PLACEHOLDER")} />
          </TabsContent>
          <TabsContent value="preview" className="min-h-64 rounded-lg border p-4">
            {field.value ? <article className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{field.value}</ReactMarkdown>
            </article> : <p className="text-sm text-muted-foreground">{t("TXT_MARKDOWN_EMPTY")}</p>}
          </TabsContent>
        </Tabs>
        {!props.disabled && <FileDropzone accept={DOCUMENT_ACCEPT} icon={FileText}
          maxFiles={1} multiple={false} title={t("TXT_REQUIREMENT_DOCUMENT_TITLE")}
          help={t("TXT_REQUIREMENT_DOCUMENT_HELP")} onReject={() => setImportError(true)}
          onAccept={async ([file]) => {
            setImportError(false);
            try {
              const content = await parseRequirementDocument(file);
              field.onChange([field.value.trim(), content].filter(Boolean).join("\n\n"));
              setTab("preview");
            } catch { setImportError(true); }
          }} />}
        <FieldError>{props.error ? t(props.error) : importError ? t("TXT_REQUIREMENT_DOCUMENT_REJECTED") : undefined}</FieldError>
      </Field>
    )} />
  );
}
