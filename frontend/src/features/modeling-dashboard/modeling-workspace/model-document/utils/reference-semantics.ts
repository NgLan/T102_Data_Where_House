import type { DbmlColumn, DbmlReference, DbmlTable } from "../dbml/types";
import { getEffectiveColumnConstraints } from "./column-constraints";

export function hasCandidateKey(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  if (reference.relation === "<>") {
    return (
      isCandidateKey(from, reference.fromColumns) &&
      isCandidateKey(to, reference.toColumns)
    );
  }
  const target = reference.relation === ">" ? to : from;
  const columns =
    reference.relation === ">" ? reference.toColumns : reference.fromColumns;
  return isCandidateKey(target, columns);
}

export function hasValidReferentialActions(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): boolean {
  const actions = [reference.onDelete, reference.onUpdate];
  if (!actions.includes("set null") && !actions.includes("set default")) {
    return true;
  }
  const foreign = findForeignColumns(reference, from, to);
  if (!foreign) return false;
  if (
    actions.includes("set null") &&
    foreign.some((column) => !column || column.isNotNull || column.isPrimaryKey)
  ) {
    return false;
  }
  return (
    !actions.includes("set default") ||
    foreign.every((column) => Boolean(column?.defaultValue.trim()))
  );
}

function isCandidateKey(table: DbmlTable, names: string[]): boolean {
  const primaryKeyNames = table.columns
    .filter((column) => column.isPrimaryKey)
    .map((column) => column.name);
  if (sameNames(primaryKeyNames, names)) return true;
  if (names.length !== 1) return false;
  const column = findColumn(table, names[0]);
  return column
    ? getEffectiveColumnConstraints(table, column).isUnique
    : false;
}

function findForeignColumns(
  reference: DbmlReference,
  from: DbmlTable,
  to: DbmlTable,
): Array<DbmlColumn | undefined> | null {
  if (reference.relation === ">") {
    return reference.fromColumns.map((name) => findColumn(from, name));
  }
  if (reference.relation === "<" || reference.relation === "-") {
    return reference.toColumns.map((name) => findColumn(to, name));
  }
  return null;
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
