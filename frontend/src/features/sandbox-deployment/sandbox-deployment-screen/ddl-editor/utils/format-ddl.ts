import { format, type SqlLanguage } from "sql-formatter";
import type { DdlDialect } from "../../../constants/supported-ddl-dialects";

const FORMATTER_LANGUAGE: Record<DdlDialect, SqlLanguage> = {
  POSTGRESQL: "postgresql",
  SNOWFLAKE: "snowflake",
  BIGQUERY: "bigquery",
};

/** Định dạng DDL bằng dialect tương ứng và không che giấu lỗi formatter. */
export function formatDdl(sql: string, dialect: DdlDialect): string {
  if (!sql) return "";
  return format(sql, {
    language: FORMATTER_LANGUAGE[dialect],
    keywordCase: "upper",
    dataTypeCase: "upper",
  });
}
