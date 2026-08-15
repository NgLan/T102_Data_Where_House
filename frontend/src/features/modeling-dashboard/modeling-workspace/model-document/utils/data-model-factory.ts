import { parseDbml } from "@/common/dbml/dbml-adapter";
import type { DbmlColumn, DbmlDocument, DbmlTable } from "@/common/dbml/types";

/** Parse DBML bắt buộc thành document cho state khởi tạo.
 * @param code DBML source hợp lệ mong đợi.
 * @returns Document do adapter thư viện tạo.
 * @throws Error khi source không hợp lệ.
 */
export function requireParsedDocument(code: string): DbmlDocument {
  const parsed = parseDbml(code);
  if (!parsed.document) throw new Error(parsed.error ?? "INVALID_DBML_CONTENT");
  return parsed.document;
}

/** Tạo bảng mới với tên không trùng trong draft.
 * @param tables Các bảng hiện hành.
 * @returns Bảng rỗng có identifier ổn định.
 */
export function createTable(tables: DbmlTable[]): DbmlTable {
  const suffix = nextSuffix(
    tables.map((table) => table.name),
    "new_table",
  );
  return {
    id: crypto.randomUUID(),
    schemaName: "public",
    name: `new_table_${suffix}`,
    note: "",
    columns: [],
    extraStatements: [],
  };
}

/** Tạo cột mới với tên không trùng trong bảng.
 * @param columns Các cột hiện hành.
 * @returns Cột varchar mặc định có identifier ổn định.
 */
export function createColumn(columns: DbmlColumn[]): DbmlColumn {
  const suffix = nextSuffix(
    columns.map((column) => column.name),
    "new_column",
  );
  return {
    id: crypto.randomUUID(),
    name: `new_column_${suffix}`,
    dataType: "varchar(255)",
    isPrimaryKey: false,
    isNotNull: false,
    isUnique: false,
    isAutoIncrement: false,
    defaultValue: "",
    note: "",
    checks: [],
    extraSettings: [],
  };
}

function nextSuffix(names: string[], prefix: string): number {
  let suffix = names.length + 1;
  while (names.includes(`${prefix}_${suffix}`)) suffix += 1;
  return suffix;
}
