export type DbmlDefaultEditorKind = "integer" | "decimal" | "boolean" | "text";

const INTEGER_TYPES = new Set(["smallint", "int", "integer", "bigint"]);
const DECIMAL_TYPES = new Set([
  "decimal",
  "numeric",
  "real",
  "float",
  "double",
  "double precision",
]);
const INTEGER_LITERAL_PATTERN = /^[+-]?\d+$/;
const DECIMAL_LITERAL_PATTERN = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/;

/** Xác định control phù hợp để chỉnh default dựa trên kiểu dữ liệu DBML.
 * @param dataType Kiểu dữ liệu đầy đủ, có thể kèm precision hoặc length.
 * @returns Nhóm control dùng cho default value.
 */
export function getDbmlDefaultEditorKind(
  dataType: string,
): DbmlDefaultEditorKind {
  const baseType = dataType.trim().toLowerCase().split("(")[0].trim();
  if (INTEGER_TYPES.has(baseType)) return "integer";
  if (DECIMAL_TYPES.has(baseType)) return "decimal";
  if (baseType === "boolean" || baseType === "bool") return "boolean";
  return "text";
}

/** Kiểm tra literal default tương thích với kiểu dữ liệu của cột.
 * @param dataType Kiểu dữ liệu DBML của cột.
 * @param defaultValue Literal hoặc biểu thức default cần kiểm tra.
 * @returns `true` khi để trống, là biểu thức DBML, hoặc literal đúng kiểu.
 */
export function isDbmlDefaultValueCompatible(
  dataType: string,
  defaultValue: string,
): boolean {
  const value = defaultValue.trim();
  if (!value || value.toLowerCase() === "null" || isDbmlExpression(value))
    return true;
  const kind = getDbmlDefaultEditorKind(dataType);
  if (kind === "integer") return INTEGER_LITERAL_PATTERN.test(value);
  if (kind === "decimal") return DECIMAL_LITERAL_PATTERN.test(value);
  if (kind === "boolean") return value === "true" || value === "false";
  return true;
}

function isDbmlExpression(value: string): boolean {
  return value.length >= 2 && value.startsWith("`") && value.endsWith("`");
}
