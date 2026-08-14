export type DdlDialect = "postgresql" | "bigquery" | "snowflake";

export interface DdlRequest {
  model_name: string;
  revision: number;
  dialect: DdlDialect;
  dbml: string;
}

export interface DdlDocument {
  model_name: string;
  revision: number;
  dialect: DdlDialect;
  content: string;
  table_count: number;
  generated_at: string;
}
