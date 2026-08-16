import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { MAX_PROJECT_NAME_LENGTH } from "@/common/constants/project-constraints";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { Textarea } from "@/common/components/ui/textarea";
import { PROJECT_DOMAIN_OPTIONS } from "../constants/project-domain-options";
import type { CreateProjectFormErrors } from "../hooks/use-create-project-form";
import type { CreateProjectFormValues } from "../schemas/create-project-form-schema";

interface CreateProjectFieldsProps {
  values: CreateProjectFormValues;
  errors: CreateProjectFormErrors;
  onFieldChange: (field: keyof CreateProjectFormValues, value: string) => void;
}

/** Các field thuần hiển thị của create form. */
export function CreateProjectFields(props: CreateProjectFieldsProps) {
  const { t } = useTranslation("project-management");
  return <>
    <FormField label={t("NAME_LABEL")} error={props.errors.name}>
      <Input autoFocus maxLength={MAX_PROJECT_NAME_LENGTH} value={props.values.name}
        onChange={(event) => props.onFieldChange("name", event.target.value)}
        placeholder={t("NAME_PLACEHOLDER")} aria-invalid={Boolean(props.errors.name)} />
    </FormField>
    <FormField label={t("DOMAIN_LABEL")} error={props.errors.domain}>
      <NativeSelect className="w-full" value={props.values.domain}
        onChange={(event) => props.onFieldChange("domain", event.target.value)}
        aria-invalid={Boolean(props.errors.domain)}>
        {PROJECT_DOMAIN_OPTIONS.map((key) => <NativeSelectOption
          key={key} value={key.toLowerCase()}>{t(`DOMAIN_${key}`)}</NativeSelectOption>)}
      </NativeSelect>
    </FormField>
    <FormField label={t("REQUIREMENT_LABEL")} error={props.errors.requirement}>
      <Textarea value={props.values.requirement}
        onChange={(event) => props.onFieldChange("requirement", event.target.value)}
        placeholder={t("REQUIREMENT_PLACEHOLDER")}
        aria-invalid={Boolean(props.errors.requirement)} />
    </FormField>
  </>;
}

function FormField(props: { label: string; error?: string; children: ReactNode }) {
  return <label className="block space-y-1.5 text-sm font-medium">
    {props.label}
    {props.children}
    {props.error && <span className="block text-xs text-destructive" role="alert">
      {props.error}
    </span>}
  </label>;
}
