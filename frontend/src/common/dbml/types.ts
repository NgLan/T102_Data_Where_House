/** Mô hình có cấu trúc dùng chung giữa ERD và trình chỉnh sửa DBML. */

export interface DbmlColumn {
  id: string;
  name: string;
  dataType: string;
  isPrimaryKey: boolean;
  isNotNull: boolean;
  isUnique: boolean;
  isAutoIncrement: boolean;
  defaultValue: string;
  note: string;
  checks: string[];
  extraSettings: string[];
}

export interface DbmlTable {
  id: string;
  schemaName: string;
  name: string;
  note: string;
  columns: DbmlColumn[];
  extraStatements: string[];
}

export interface DbmlReference {
  id: string;
  fromSchema: string;
  fromTable: string;
  fromColumn: string;
  fromColumns: string[];
  relation: '>' | '<' | '-' | '<>';
  toSchema: string;
  toTable: string;
  toColumn: string;
  toColumns: string[];
  name?: string;
  onDelete?: DbmlReferentialAction;
  onUpdate?: DbmlReferentialAction;
}

export type DbmlReferentialAction =
  | 'cascade'
  | 'restrict'
  | 'set null'
  | 'set default'
  | 'no action';

export interface DbmlDocument {
  preamble: string;
  tables: DbmlTable[];
  references: DbmlReference[];
  sourceModel: unknown;
}

export interface DbmlParseResult {
  document: DbmlDocument | null;
  error: string | null;
}
