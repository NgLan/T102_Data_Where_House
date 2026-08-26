import type { UseFormReturn } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import { NativeSelect, NativeSelectOption } from "@/common/components/ui/native-select";
import { Textarea } from "@/common/components/ui/textarea";
import { cn } from "@/common/lib/utils";
import {
  CUSTOM_PROJECT_DOMAIN,
  PROJECT_DOMAIN_OPTIONS,
} from "@/common/projects/project-domain-options";
import type { ProjectDetailsValues } from "./project-details/schemas/project-details-schema";

interface ProjectDetailsFormProps {
  disabled: boolean;
  form: UseFormReturn<ProjectDetailsValues>;
}

/** Project information được lưu cùng workflow chính của Project Init. */
export function ProjectDetailsForm(props: ProjectDetailsFormProps) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  const domain = props.form.watch("domain");
  const knownDomain = PROJECT_DOMAIN_OPTIONS.some(({ value }) => value === domain);
  return (
    <section className="space-y-5 rounded-xl border bg-background p-5">
      <header>
        <h2 className="font-semibold">{t("TXT_PROJECT_SECTION_TITLE")}</h2>
        <p className="text-sm text-muted-foreground">{t("TXT_PROJECT_SECTION_SUBTITLE")}</p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        <Field data-invalid={Boolean(props.form.formState.errors.name)}>
          <FieldLabel htmlFor="project-name">{t("PROJECT_NAME_LABEL")}</FieldLabel>
          <Input id="project-name" disabled={props.disabled} {...props.form.register("name")} aria-invalid={Boolean(props.form.formState.errors.name)} placeholder={t("PROJECT_NAME_PLACEHOLDER")} />
          <FieldError>{props.form.formState.errors.name && t("MSG_PROJECT_INVALID")}</FieldError>
        </Field>
        <Field data-invalid={Boolean(props.form.formState.errors.domain)}>
          <FieldLabel htmlFor="project-domain">{t("DOMAIN_LABEL")}</FieldLabel>
          <NativeSelect id="project-domain" disabled={props.disabled} {...props.form.register("domain")} className={cn("w-full", !domain && "[&>select]:text-muted-foreground")} aria-invalid={Boolean(props.form.formState.errors.domain)}>
            <NativeSelectOption value="">{t("DOMAIN_PLACEHOLDER")}</NativeSelectOption>
            {PROJECT_DOMAIN_OPTIONS.filter(({ value }) => value !== CUSTOM_PROJECT_DOMAIN).map((option) => (
              <NativeSelectOption key={option.value} value={option.value}>{tCommon(option.labelKey)}</NativeSelectOption>
            ))}
            {!knownDomain && domain && <NativeSelectOption value={domain}>{domain}</NativeSelectOption>}
          </NativeSelect>
          <FieldError>{props.form.formState.errors.domain && t("MSG_PROJECT_DOMAIN_MAX")}</FieldError>
        </Field>
      </div>
      <Field>
        <FieldLabel htmlFor="project-description">{t("DESCRIPTION_LABEL")}</FieldLabel>
        <Textarea
          id="project-description"
          rows={3}
          disabled={props.disabled}
          placeholder={t("DESCRIPTION_PLACEHOLDER")}
          {...props.form.register("description")}
        />
      </Field>
    </section>
  );
}
