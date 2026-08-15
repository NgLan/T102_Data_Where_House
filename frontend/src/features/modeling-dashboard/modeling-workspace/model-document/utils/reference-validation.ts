import { canonicalDbmlDataType } from "@/common/dbml/data-type";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlReference,
  DbmlTable,
} from "@/common/dbml/types";
import type { DataModelValidationErrors } from "../types/data-model-validation-types";
import { getEffectiveColumnConstraints } from "./column-constraints";

interface ReferenceContext {
  document: DbmlDocument;
  reference: DbmlReference;
  index: number;
  errors: DataModelValidationErrors;
}

/** Kiểm tra endpoint và semantic constraint của một DBML reference. */
export function validateReference(context: ReferenceContext): void {
  const { document, reference, index, errors } = context;
  const from = findTable(document, reference.fromSchema, reference.fromTable);
  const to = findTable(document, reference.toSchema, reference.toTable);
  const path = `references.${index}`;
  if (!hasMatchingArity(reference))
    errors[`${path}.columns`] = "INVALID_RELATIONSHIP_COLUMNS";
  if (!from || !to || hasMissingColumns(reference, from, to)) {
    errors[`${path}.columns`] = "INVALID_RELATIONSHIP_ENDPOINT";
    return;
  }
  if (!hasCompatibleTypes(reference, from, to))
    errors[`${path}.columns`] = "INVALID_RELATIONSHIP_DATA_TYPE";
  if (!hasCandidateKey(reference, from, to))
    errors[path] = "INVALID_RELATIONSHIP_TARGET_KEY";
  if (!hasValidReferentialActions(reference, from, to))
    errors[path] = "INVALID_REFERENTIAL_ACTION";
  if (hasDuplicateReference(document, reference))
    errors[path] = "DUPLICATE_RELATIONSHIP";
}

function hasMatchingArity(reference: DbmlReference): boolean {
  return (
    reference.fromColumns.length > 0 &&
    reference.fromColumns.length === reference.toColumns.length
  );
}

function hasMissingColumns(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  return (
    reference.fromColumns.some((name) => !findColumn(from, name)) ||
    reference.toColumns.some((name) => !findColumn(to, name))
  );
}

function hasCompatibleTypes(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  return reference.fromColumns.every((name, index) => {
    const fromType = findColumn(from, name)?.dataType ?? "";
    const toType = findColumn(to, reference.toColumns[index])?.dataType ?? "";
    return canonicalDbmlDataType(fromType) === canonicalDbmlDataType(toType);
  });
}

function hasCandidateKey(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  if (reference.relation === "<>")
    return (
      isCandidateKey(from, reference.fromColumns) &&
      isCandidateKey(to, reference.toColumns)
    );
  const target = reference.relation === ">" ? to : from;
  const columns =
    reference.relation === ">" ? reference.toColumns : reference.fromColumns;
  return isCandidateKey(target, columns);
}

function isCandidateKey(table: DbmlTable, names: string[]): boolean {
  const primaryKeyNames = table.columns
    .filter((column) => column.isPrimaryKey)
    .map((column) => column.name);
  if (sameNames(primaryKeyNames, names)) return true;
  if (names.length !== 1) return false;
  const column = findColumn(table, names[0]);
  return column ? getEffectiveColumnConstraints(table, column).isUnique : false;
}

function hasValidReferentialActions(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  const actions = [reference.onDelete, reference.onUpdate];
  if (!actions.includes("set null") && !actions.includes("set default"))
    return true;
  const foreign =
    reference.relation === ">"
      ? [from, reference.fromColumns]
      : reference.relation === "<" || reference.relation === "-"
        ? [to, reference.toColumns]
        : null;
  if (!foreign) return false;
  const columns = (foreign[1] as string[]).map((name) =>
    findColumn(foreign[0] as DbmlTable, name),
  );
  if (
    actions.includes("set null") &&
    columns.some((column) => !column || column.isNotNull || column.isPrimaryKey)
  )
    return false;
  return (
    !actions.includes("set default") ||
    columns.every((column) => Boolean(column?.defaultValue.trim()))
  );
}

function hasDuplicateReference(
  document: DbmlDocument,
  reference: DbmlReference,
): boolean {
  const signature = referenceSignature(reference);
  return document.references.some(
    (item) =>
      item.id !== reference.id && referenceSignature(item) === signature,
  );
}

function referenceSignature(reference: DbmlReference): string {
  return [
    reference.fromSchema,
    reference.fromTable,
    reference.fromColumns.join(","),
    reference.relation,
    reference.toSchema,
    reference.toTable,
    reference.toColumns.join(","),
  ]
    .join("|")
    .toLowerCase();
}

function findTable(
  document: DbmlDocument,
  schema: string,
  name: string,
): DbmlTable | undefined {
  return document.tables.find(
    (table) => table.schemaName === schema && table.name === name,
  );
}

function findColumn(table: DbmlTable, name: string): DbmlColumn | undefined {
  return table.columns.find((column) => column.name === name);
}

function sameNames(left: string[], right: string[]): boolean {
  return (
    left.length > 0 &&
    left.length === right.length &&
    left.every((name, index) => name === right[index])
  );
}
