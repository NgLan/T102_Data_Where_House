import {
  isApiError,
  isApiValidationError,
  type ApiError,
} from "@/api";
import type { UseFormReturn } from "react-hook-form";
import type { SandboxConfigFormValues } from "../schemas/sandbox-config-form-schema";

const API_TO_FORM_FIELD: Record<string, keyof SandboxConfigFormValues> = {
  host: "host",
  port: "port",
  database_name: "databaseName",
  username: "username",
  password: "password",
  schema_name: "schemaName",
};

/** Gắn validation details của Backend vào đúng field trên form. */
export function applySandboxConfigApiErrors(
  error: unknown,
  form: UseFormReturn<SandboxConfigFormValues>,
): ApiError | null {
  if (!isApiError(error)) return null;
  if (!isApiValidationError(error)) return error;
  error.details.forEach((detail) => {
    const apiField = detail.field.split(".").at(-1) ?? detail.field;
    const formField = API_TO_FORM_FIELD[apiField];
    if (formField) {
      form.setError(formField, { type: "server", message: "MSG_CONFIG_INVALID" });
    }
  });
  return error;
}
