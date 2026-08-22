"use client";

import { useFormContext } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import { NativeSelect, NativeSelectOption } from "@/common/components/ui/native-select";
import { Textarea } from "@/common/components/ui/textarea";
import {
  CUSTOM_PROJECT_DOMAIN,
  PROJECT_DOMAIN_OPTIONS,
} from "@/common/projects/project-domain-options";
import type { CreateProjectFormValues } from "../schemas/create-project-form-schema";

/** Hiển thị các field của form tạo Project từ FormProvider.
 * @returns Field group có label, control và validation error truy cập được.
 */
export function CreateProjectFields() {
  const { t } = useTranslation("project-management");
  const { t: tCommon } = useTranslation("common");
  const form = useFormContext<CreateProjectFormValues>();
  const selectedDomain = form.watch("domainSelection");
  return (
    <FieldGroup>
      <TextField name="name" label={t("NAME_LABEL")} placeholder={t("NAME_PLACEHOLDER")} autoFocus />
      <Field data-invalid={Boolean(form.formState.errors.domainSelection)}>
        <FieldLabel htmlFor="project-domain">{t("DOMAIN_LABEL")}</FieldLabel>
        <NativeSelect id="project-domain" className="w-full" {...form.register("domainSelection")}
          aria-invalid={Boolean(form.formState.errors.domainSelection)}>
          {PROJECT_DOMAIN_OPTIONS.map((option) => (
            <NativeSelectOption key={option.value} value={option.value}>
              {tCommon(option.labelKey)}
            </NativeSelectOption>
          ))}
        </NativeSelect>
        <FieldError>{translateError(t, form.formState.errors.domainSelection?.message)}</FieldError>
      </Field>
      {selectedDomain === CUSTOM_PROJECT_DOMAIN && (
        <TextField name="customDomain" label={t("CUSTOM_DOMAIN_LABEL")}
          placeholder={t("CUSTOM_DOMAIN_PLACEHOLDER")} />
      )}
      <Field data-invalid={Boolean(form.formState.errors.description)}>
        <FieldLabel htmlFor="project-description">{t("DESCRIPTION_LABEL")}</FieldLabel>
        <Textarea id="project-description" {...form.register("description")}
          placeholder={t("DESCRIPTION_PLACEHOLDER")}
          aria-invalid={Boolean(form.formState.errors.description)} />
        <FieldError>{translateError(t, form.formState.errors.description?.message)}</FieldError>
      </Field>
    </FieldGroup>
  );
}

interface TextFieldProps {
  name: "name" | "customDomain";
  label: string;
  placeholder: string;
  autoFocus?: boolean;
}

function TextField({ name, label, placeholder, autoFocus }: TextFieldProps) {
  const { t } = useTranslation("project-management");
  const form = useFormContext<CreateProjectFormValues>();
  const error = form.formState.errors[name];
  const id = `project-${name}`;
  return (
    <Field data-invalid={Boolean(error)}>
      <FieldLabel htmlFor={id}>{label}</FieldLabel>
      <Input id={id} autoFocus={autoFocus} {...form.register(name)} placeholder={placeholder}
        aria-invalid={Boolean(error)} />
      <FieldError>{translateError(t, error?.message)}</FieldError>
    </Field>
  );
}

function translateError(translate: (key: string) => string, error?: string): string | undefined {
  return error ? translate(error) : undefined;
}
