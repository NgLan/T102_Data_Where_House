import { useTranslation } from "react-i18next";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { Textarea } from "@/common/components/ui/textarea";
import type {
  ProjectDetailsErrors,
  ProjectDetailsField,
  ProjectDetailsValues,
} from "../schemas/project-details-schema";

interface ProjectDetailsFormProps {
  form: ProjectDetailsValues;
  errors: ProjectDetailsErrors;
  disabled: boolean;
  onChange: (field: ProjectDetailsField, value: string) => void;
}

/** Form thông tin dự án, không chứa cấu hình dialect thuộc modeling step.
 * @param props Giá trị form, lỗi validation, trạng thái và callback thay đổi.
 * @returns Form chỉnh tên, domain và requirement của Project.
 */
export function ProjectDetailsForm(props: ProjectDetailsFormProps) {
  const { t } = useTranslation("project-init");
  return (
    <section className="space-y-5 rounded-xl border bg-background p-5">
      <div>
        <h2 className="font-semibold">{t("TXT_PROJECT_SECTION_TITLE")}</h2>
        <p className="text-sm text-muted-foreground">
          {t("TXT_PROJECT_SECTION_SUBTITLE")}
        </p>
      </div>
      <Field
        label={t("LBL_PROJECT_NAME")}
        error={translateError(t, props.errors.name)}
      >
        <Input
          value={props.form.name}
          disabled={props.disabled}
          aria-invalid={Boolean(props.errors.name)}
          placeholder={t("PH_PROJECT_NAME")}
          onChange={(event) => props.onChange("name", event.target.value)}
        />
      </Field>
      <Field
        label={t("LBL_DOMAIN")}
        error={translateError(t, props.errors.domain)}
      >
        <NativeSelect
          className="w-full"
          value={props.form.domain}
          disabled={props.disabled}
          aria-invalid={Boolean(props.errors.domain)}
          onChange={(event) => props.onChange("domain", event.target.value)}
        >
          <NativeSelectOption value="">{t("PH_DOMAIN")}</NativeSelectOption>
          <NativeSelectOption value="ride">
            {t("TXT_DOMAIN_RIDE")}
          </NativeSelectOption>
          <NativeSelectOption value="ecommerce">
            {t("TXT_DOMAIN_ECOMMERCE")}
          </NativeSelectOption>
          <NativeSelectOption value="banking">
            {t("TXT_DOMAIN_BANKING")}
          </NativeSelectOption>
          <NativeSelectOption value="custom">
            {t("TXT_DOMAIN_CUSTOM")}
          </NativeSelectOption>
        </NativeSelect>
      </Field>
      <Field
        label={t("LBL_REQUIREMENT")}
        error={translateError(t, props.errors.requirement)}
      >
        <Textarea
          rows={7}
          value={props.form.requirement}
          disabled={props.disabled}
          aria-invalid={Boolean(props.errors.requirement)}
          placeholder={t("PH_REQUIREMENT")}
          onChange={(event) =>
            props.onChange("requirement", event.target.value)
          }
        />
      </Field>
    </section>
  );
}

function Field(props: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-2 text-sm font-medium">
      <span>{props.label}</span>
      {props.children}
      {props.error && (
        <span className="block text-xs text-destructive">{props.error}</span>
      )}
    </label>
  );
}

function translateError(t: (key: string) => string, key?: string) {
  return key ? t(key) : undefined;
}
