import { ArrowRight } from "lucide-react";
import type { UseFormReturn } from "react-hook-form";
import { useTranslation } from "react-i18next";
import type { ProjectRequirementResponse } from "@/api";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { cn } from "@/common/lib/utils";
import {
  CUSTOM_PROJECT_DOMAIN,
  PROJECT_DOMAIN_OPTIONS,
} from "@/common/projects/project-domain-options";
import type { ProjectDetailsValues } from "./project-details/schemas/project-details-schema";
import { RawRequirementField } from "./project-details/components/RawRequirementField";
import { StructuredRequirementsTable } from "./project-details/components/StructuredRequirementsTable";

interface ProjectDetailsFormProps {
  disabled: boolean;
  form: UseFormReturn<ProjectDetailsValues>;
  requirements: ProjectRequirementResponse[];
}

/** Form Raw Requirement và thông tin Project; Structured Requirements chỉ đọc. */
export function ProjectDetailsForm({
  disabled,
  form,
  requirements,
}: ProjectDetailsFormProps) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  const domain = form.watch("domain");
  const knownDomain = PROJECT_DOMAIN_OPTIONS.some(
    ({ value }) => value === domain,
  );
  return (
    <section className="space-y-5 rounded-xl border bg-background p-5">
      <header>
        <h2 className="font-semibold">{t("TXT_PROJECT_SECTION_TITLE")}</h2>
        <p className="text-sm text-muted-foreground">
          {t("TXT_PROJECT_SECTION_SUBTITLE")}
        </p>
      </header>
      <Field data-invalid={Boolean(form.formState.errors.name)}>
        <FieldLabel htmlFor="project-name">
          {t("PROJECT_NAME_LABEL")}
        </FieldLabel>
        <Input
          id="project-name"
          disabled={disabled}
          {...form.register("name")}
          aria-invalid={Boolean(form.formState.errors.name)}
          placeholder={t("PROJECT_NAME_PLACEHOLDER")}
        />
        <FieldError>
          {form.formState.errors.name && t("MSG_PROJECT_INVALID")}
        </FieldError>
      </Field>
      <Field data-invalid={Boolean(form.formState.errors.domain)}>
        <FieldLabel htmlFor="project-domain">{t("DOMAIN_LABEL")}</FieldLabel>
        <NativeSelect
          id="project-domain"
          disabled={disabled}
          {...form.register("domain")}
          className={cn(
            "w-full",
            !domain && "[&>select]:text-muted-foreground",
          )}
          aria-invalid={Boolean(form.formState.errors.domain)}
        >
          <NativeSelectOption value="">
            {t("DOMAIN_PLACEHOLDER")}
          </NativeSelectOption>
          {PROJECT_DOMAIN_OPTIONS.filter(
            ({ value }) => value !== CUSTOM_PROJECT_DOMAIN,
          ).map((option) => (
            <NativeSelectOption key={option.value} value={option.value}>
              {tCommon(option.labelKey)}
            </NativeSelectOption>
          ))}
          {!knownDomain && domain && (
            <NativeSelectOption value={domain}>{domain}</NativeSelectOption>
          )}
        </NativeSelect>
        <FieldError>
          {form.formState.errors.domain && t("MSG_PROJECT_DOMAIN_MAX")}
        </FieldError>
      </Field>
      <div className="grid items-stretch gap-3 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1.4fr)]">
        <RawRequirementField
          control={form.control}
          disabled={disabled}
          error={
            form.formState.errors.requirement
              ? "MSG_PROJECT_REQUIREMENT_MIN"
              : undefined
          }
        />
        <div
          className="flex items-center justify-center text-muted-foreground"
          aria-hidden
        >
          <ArrowRight className="size-6 rotate-90 lg:rotate-0" />
        </div>
        <StructuredRequirementsTable items={requirements} />
      </div>
    </section>
  );
}
