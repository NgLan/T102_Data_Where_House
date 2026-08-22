import type { SandboxDbType } from "@/api";

/** Các dialect mà Backend hiện hỗ trợ sinh DDL. */
export const SUPPORTED_DDL_DIALECTS = [
  "POSTGRESQL",
  "SNOWFLAKE",
  "BIGQUERY",
] as const satisfies readonly SandboxDbType[];

export type DdlDialect = (typeof SUPPORTED_DDL_DIALECTS)[number];

/** Engine duy nhất mà Sandbox executor hiện hỗ trợ. */
export const SANDBOX_DB_TYPE = "POSTGRESQL" satisfies SandboxDbType;

/** Kiểm tra generated enum có thuộc tập dialect hiển thị hay không. */
export function isDdlDialect(value: string): value is DdlDialect {
  return SUPPORTED_DDL_DIALECTS.some((dialect) => dialect === value);
}
