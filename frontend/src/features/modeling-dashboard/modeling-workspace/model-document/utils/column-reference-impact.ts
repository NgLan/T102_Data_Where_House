import { canonicalDbmlDataType } from "../dbml/data-type";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlReference,
  DbmlTable,
} from "../dbml/types";

interface TypeChangeInput {
  document: DbmlDocument;
  table: DbmlTable;
  column: DbmlColumn;
  nextDataType: string;
}

export function getColumnReferences(
  document: DbmlDocument,
  table: DbmlTable,
  column: DbmlColumn,
): DbmlReference[] {
  return document.references.filter(
    (reference) =>
      matchesEndpoint(reference, "from", table, column) ||
      matchesEndpoint(reference, "to", table, column),
  );
}

export function findIncompatibleReferenceIds(input: TypeChangeInput): string[] {
  return input.document.references.flatMap((reference) => {
    const counterpart = findCounterpartColumn(input, reference);
    const isCompatible =
      !counterpart ||
      canonicalDbmlDataType(counterpart.dataType) ===
        canonicalDbmlDataType(input.nextDataType);
    return isCompatible ? [] : [reference.id];
  });
}

function findCounterpartColumn(
  input: TypeChangeInput,
  reference: DbmlReference,
): DbmlColumn | null {
  const fromIndex = endpointIndex(reference, "from", input.table, input.column);
  if (fromIndex >= 0) {
    return findColumn(input.document, {
      schema: reference.toSchema,
      table: reference.toTable,
      column: reference.toColumns[fromIndex],
    });
  }
  const toIndex = endpointIndex(reference, "to", input.table, input.column);
  if (toIndex < 0) return null;
  return findColumn(input.document, {
    schema: reference.fromSchema,
    table: reference.fromTable,
    column: reference.fromColumns[toIndex],
  });
}

function endpointIndex(
  reference: DbmlReference,
  side: "from" | "to",
  table: DbmlTable,
  column: DbmlColumn,
): number {
  const prefix = side === "from" ? "from" : "to";
  const schema = reference[`${prefix}Schema`];
  const tableName = reference[`${prefix}Table`];
  const columns = reference[`${prefix}Columns`];
  return schema === table.schemaName && tableName === table.name
    ? columns.indexOf(column.name)
    : -1;
}

function matchesEndpoint(
  reference: DbmlReference,
  side: "from" | "to",
  table: DbmlTable,
  column: DbmlColumn,
): boolean {
  return endpointIndex(reference, side, table, column) >= 0;
}

function findColumn(
  document: DbmlDocument,
  address: { schema: string; table: string; column: string },
): DbmlColumn | null {
  return (
    document.tables
      .find(
        (table) =>
          table.schemaName === address.schema && table.name === address.table,
      )
      ?.columns.find((column) => column.name === address.column) ?? null
  );
}
