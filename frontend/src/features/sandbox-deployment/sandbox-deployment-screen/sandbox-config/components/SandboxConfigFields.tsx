import type { HTMLInputTypeAttribute } from "react";
import type { UseFormReturn, UseFormRegisterReturn } from "react-hook-form";
import { useTranslation } from "react-i18next";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import type { SandboxConfigFormValues } from "../schemas/sandbox-config-form-schema";

interface SandboxConfigFieldsProps {
  disabled: boolean;
  form: UseFormReturn<SandboxConfigFormValues>;
}

/** Hiển thị các input connection và lỗi validation theo field. */
export function SandboxConfigFields(props: SandboxConfigFieldsProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <ConfigField id="sandbox-host" label={t("HOST_LABEL")} error={props.form.formState.errors.host?.message} registration={props.form.register("host")} disabled={props.disabled} />
      <ConfigField id="sandbox-port" label={t("PORT_LABEL")} type="number" error={props.form.formState.errors.port?.message} registration={props.form.register("port", { valueAsNumber: true })} disabled={props.disabled} />
      <ConfigField id="sandbox-database" label={t("DATABASE_NAME_LABEL")} error={props.form.formState.errors.databaseName?.message} registration={props.form.register("databaseName")} disabled={props.disabled} />
      <ConfigField id="sandbox-schema" label={t("SCHEMA_NAME_LABEL")} error={props.form.formState.errors.schemaName?.message} registration={props.form.register("schemaName")} disabled={props.disabled} />
      <ConfigField id="sandbox-username" label={t("USERNAME_LABEL")} error={props.form.formState.errors.username?.message} registration={props.form.register("username")} disabled={props.disabled} />
      <ConfigField id="sandbox-password" label={t("PASSWORD_LABEL")} type="password" description={t("TXT_PASSWORD_DESCRIPTION")} error={props.form.formState.errors.password?.message} registration={props.form.register("password")} disabled={props.disabled} />
    </div>
  );
}

interface ConfigFieldProps {
  id: string;
  label: string;
  disabled: boolean;
  registration: UseFormRegisterReturn;
  description?: string;
  error?: string;
  type?: HTMLInputTypeAttribute;
}

function ConfigField(props: ConfigFieldProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <Field data-invalid={Boolean(props.error)}>
      <FieldLabel htmlFor={props.id}>{props.label}</FieldLabel>
      <Input id={props.id} type={props.type} disabled={props.disabled} aria-invalid={Boolean(props.error)} className="font-mono" {...props.registration} />
      {props.description && <FieldDescription>{props.description}</FieldDescription>}
      <FieldError>{props.error ? t(props.error) : null}</FieldError>
    </Field>
  );
}
