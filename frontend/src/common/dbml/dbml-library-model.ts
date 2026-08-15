/** Kiểu tối thiểu của model do @dbml/core công bố, cô lập khỏi view model ứng dụng. */
export interface DatabaseModel {
  tables: TableModel[];
  refs: ReferenceModel[];
  [key: string]: unknown;
}

export interface TableModel {
  name: string;
  schemaName?: string | null;
  note?: { value?: string } | string | null;
  fields: FieldModel[];
  [key: string]: unknown;
}

export interface FieldModel {
  name: string;
  type: { type_name: string; schemaName?: string | null; args?: string | null };
  unique?: boolean;
  pk?: boolean;
  not_null?: boolean;
  note?: { value?: string } | string | null;
  dbdefault?: { type: string; value: unknown };
  increment?: boolean;
  checks?: Array<{ expression: string }>;
  [key: string]: unknown;
}

export interface EndpointModel {
  schemaName?: string | null;
  tableName: string;
  fieldNames: string[];
  relation: "1" | "*";
  [key: string]: unknown;
}

export interface ReferenceModel {
  endpoints: EndpointModel[];
  name?: string | null;
  onDelete?: string;
  onUpdate?: string;
  [key: string]: unknown;
}

export function emptyTableModel(): TableModel {
  return {
    name: "",
    schemaName: null,
    alias: null,
    fields: [],
    indexes: [],
    checks: [],
    partials: [],
  };
}

export function emptyFieldModel(): FieldModel {
  return {
    name: "",
    type: { schemaName: null, type_name: "varchar(255)", args: null },
  };
}
