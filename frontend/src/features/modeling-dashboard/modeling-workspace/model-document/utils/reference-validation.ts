import { canonicalDbmlDataType } from "../dbml/data-type";
import type { DbmlDocument, DbmlReference, DbmlTable } from "../dbml/types";
import type { DataModelValidationErrors } from "../types/data-model-validation-types";
import { hasDuplicateReference } from "./reference-identity";
import {
  hasCandidateKey,
  hasValidReferentialActions,
} from "./reference-semantics";

interface ReferenceContext {
  document: DbmlDocument;
  reference: DbmlReference;
  index: number;
  errors: DataModelValidationErrors;
}

export function validateReference(context: ReferenceContext): void {
  const { document, reference, index, errors } = context;
  const from = findTable(document, reference.fromSchema, reference.fromTable);
  const to = findTable(document, reference.toSchema, reference.toTable);
  const path = `references.${index}`;
  if (!hasMatchingArity(reference)) {
    errors[`${path}.columns`] = "MSG_INVALID_RELATIONSHIP_COLUMNS";
  }
  if (!from || !to || hasMissingColumns(reference, from, to)) {
    errors[`${path}.columns`] = "MSG_INVALID_RELATIONSHIP_ENDPOINT";
    return;
  }
  if (!hasCompatibleTypes(reference, from, to)) {
    errors[`${path}.columns`] = "MSG_INVALID_RELATIONSHIP_DATA_TYPE";
  }
  if (!hasCandidateKey(reference, from, to)) {
    errors[path] = "MSG_INVALID_RELATIONSHIP_TARGET_KEY";
  }
  if (!hasValidReferentialActions(reference, from, to)) {
    errors[path] = "MSG_INVALID_REFERENTIAL_ACTION";
  }
  if (hasDuplicateReference(document, reference)) {
    errors[path] = "MSG_DUPLICATE_RELATIONSHIP";
  }
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

function findTable(
  document: DbmlDocument,
  schema: string,
  name: string,
): DbmlTable | undefined {
  return document.tables.find(
    (table) => table.schemaName === schema && table.name === name,
  );
}

function findColumn(table: DbmlTable, name: string) {
  return table.columns.find((column) => column.name === name);
}
