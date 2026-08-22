import {
  zSandboxConfigRequest,
  type SandboxConfigRequest,
  type SandboxConfigResponse,
} from "@/api";
import { z } from "zod";
import { SANDBOX_DB_TYPE } from "../../../constants/supported-ddl-dialects";

export interface SandboxConfigFormValues {
  host: string;
  port: number;
  databaseName: string;
  username: string;
  password: string;
  schemaName: string;
}

export const DEFAULT_SANDBOX_CONFIG: SandboxConfigFormValues = {
  host: "127.0.0.1",
  port: 5432,
  databaseName: "sandbox_db",
  username: "postgres",
  password: "",
  schemaName: "public",
};

/** Schema form ủy quyền constraints API cho generated Zod schema. */
export const sandboxConfigFormSchema = z
  .object({
    host: z.string(),
    port: z.number(),
    databaseName: z.string(),
    username: z.string(),
    password: z.string(),
    schemaName: z.string(),
  })
  .superRefine((values, context) => {
    const result = parseSandboxConfigForm(values);
    if (result.success) return;
    result.error.issues.forEach((issue) =>
      context.addIssue({
        code: "custom",
        message: sandboxConfigIssueKey(issue.path[0]),
        path: [toFormField(issue.path[0])],
      }),
    );
  });

/** Chuẩn hóa form thành generated request; password rỗng được gửi null. */
export function parseSandboxConfigForm(values: SandboxConfigFormValues) {
  return zSandboxConfigRequest.safeParse({
    db_type: SANDBOX_DB_TYPE,
    host: values.host.trim(),
    port: values.port,
    database_name: values.databaseName.trim(),
    username: values.username.trim() || null,
    password: values.password || null,
    schema_name: values.schemaName.trim(),
  });
}

/** Ánh xạ config response sang giá trị input mà không giả lập password. */
export function toSandboxConfigFormValues(
  config: SandboxConfigResponse | null,
): SandboxConfigFormValues {
  if (!config) return DEFAULT_SANDBOX_CONFIG;
  return {
    host: config.host,
    port: config.port,
    databaseName: config.database_name,
    username: config.username ?? "",
    password: "",
    schemaName: config.schema_name ?? "public",
  };
}

/** Trả payload đã parse hoặc null khi form chưa hợp lệ. */
export function toSandboxConfigRequest(
  values: SandboxConfigFormValues,
): SandboxConfigRequest | null {
  const result = parseSandboxConfigForm(values);
  return result.success ? result.data : null;
}

function toFormField(field: PropertyKey | undefined): string {
  const fields: Record<string, keyof SandboxConfigFormValues> = {
    database_name: "databaseName",
    schema_name: "schemaName",
  };
  return fields[String(field)] ?? String(field);
}

function sandboxConfigIssueKey(field: PropertyKey | undefined): string {
  const keys: Record<string, string> = {
    host: "MSG_HOST_INVALID",
    port: "MSG_PORT_INVALID",
    database_name: "MSG_DATABASE_NAME_INVALID",
    username: "MSG_USERNAME_INVALID",
    schema_name: "MSG_SCHEMA_NAME_INVALID",
  };
  return keys[String(field)] ?? "MSG_CONFIG_INVALID";
}
