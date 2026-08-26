"use client";

import { useState } from "react";
import { Controller, type Control } from "react-hook-form";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTranslation } from "react-i18next";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/common/components/ui/tabs";
import { Textarea } from "@/common/components/ui/textarea";
import type { ProjectDetailsValues } from "../schemas/project-details-schema";

interface RawRequirementFieldProps {
  control: Control<ProjectDetailsValues>;
  disabled: boolean;
  error?: string;
  isDirty: boolean;
  onSaveDraft: () => void;
}

/** Editor Markdown giữ draft local; Ctrl/Cmd+S chỉ lưu nháp. */
export function RawRequirementField(props: RawRequirementFieldProps) {
  const { t } = useTranslation("project-init");
  const [tab, setTab] = useState("edit");
  return (
    <Controller
      name="requirement"
      control={props.control}
      render={({ field }) => (
        <Field className="flex h-[58vh] min-h-[28rem] flex-col" data-invalid={Boolean(props.error)}>
          <div className="flex items-center justify-between gap-3">
            <FieldLabel htmlFor="project-requirement">{t("REQUIREMENT_LABEL")}</FieldLabel>
            <span className="text-xs text-muted-foreground">
              {t(props.isDirty ? "TXT_RAW_UNSAVED" : "TXT_RAW_SAVED")}
            </span>
          </div>
          <Tabs value={tab} onValueChange={setTab} className="flex min-h-0 flex-1 flex-col">
            <TabsList className="w-fit">
              <TabsTrigger value="edit">{t("TXT_REQUIREMENT_EDIT_TAB")}</TabsTrigger>
              <TabsTrigger value="preview">{t("TXT_REQUIREMENT_PREVIEW_TAB")}</TabsTrigger>
            </TabsList>
            <TabsContent value="edit" className="min-h-0 flex-1">
              <Textarea
                id="project-requirement"
                className="h-full min-h-0 resize-none"
                disabled={props.disabled}
                value={field.value}
                onChange={field.onChange}
                onKeyDown={(event) => {
                  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
                    event.preventDefault();
                    props.onSaveDraft();
                  }
                }}
                placeholder={t("REQUIREMENT_OPTIONAL_PLACEHOLDER")}
              />
            </TabsContent>
            <TabsContent value="preview" className="min-h-0 flex-1 overflow-y-auto rounded-lg border p-4">
              {field.value ? (
                <article className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{field.value}</ReactMarkdown>
                </article>
              ) : (
                <p className="text-sm text-muted-foreground">{t("TXT_MARKDOWN_EMPTY")}</p>
              )}
            </TabsContent>
          </Tabs>
          <FieldError>{props.error ? t(props.error) : undefined}</FieldError>
        </Field>
      )}
    />
  );
}
