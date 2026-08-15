import type { DbmlReference } from "./types";
import type { EndpointModel, ReferenceModel } from "./dbml-library-model";

/** Ánh xạ relationship của thư viện sang ký hiệu DBML công khai. */
export function mapReference(
  reference: ReferenceModel,
  index: number,
): DbmlReference {
  const [from, to] = reference.endpoints;
  return {
    id: `source-ref-${index}`,
    fromSchema: from.schemaName ?? "public",
    fromTable: from.tableName,
    fromColumn: from.fieldNames[0] ?? "",
    fromColumns: [...from.fieldNames],
    relation: mapRelation(from.relation, to.relation),
    toSchema: to.schemaName ?? "public",
    toTable: to.tableName,
    toColumn: to.fieldNames[0] ?? "",
    toColumns: [...to.fieldNames],
    name: reference.name ?? undefined,
    onDelete: toReferentialAction(reference.onDelete),
    onUpdate: toReferentialAction(reference.onUpdate),
  };
}

/** Ánh xạ relationship editor về raw model để exporter giữ đúng metadata. */
export function toReferenceModel(reference: DbmlReference): ReferenceModel {
  const relations = endpointRelations(reference.relation);
  return {
    name: reference.name || null,
    schemaName: reference.fromSchema === "public" ? null : reference.fromSchema,
    onDelete: reference.onDelete,
    onUpdate: reference.onUpdate,
    endpoints: [
      endpoint({
        schema: reference.fromSchema,
        table: reference.fromTable,
        columns: reference.fromColumns,
        fallbackColumn: reference.fromColumn,
        relation: relations[0],
      }),
      endpoint({
        schema: reference.toSchema,
        table: reference.toTable,
        columns: reference.toColumns,
        fallbackColumn: reference.toColumn,
        relation: relations[1],
      }),
    ],
  };
}

interface EndpointInput {
  schema: string;
  table: string;
  columns: string[];
  fallbackColumn: string;
  relation: "1" | "*";
}

function endpoint(input: EndpointInput): EndpointModel {
  return {
    schemaName: input.schema === "public" ? null : input.schema,
    tableName: input.table,
    fieldNames: input.columns.length ? input.columns : [input.fallbackColumn],
    relation: input.relation,
  };
}

function mapRelation(
  from: "1" | "*",
  to: "1" | "*",
): DbmlReference["relation"] {
  if (from === "*" && to === "*") return "<>";
  if (from === "*") return ">";
  if (to === "*") return "<";
  return "-";
}

function endpointRelations(
  relation: DbmlReference["relation"],
): ["1" | "*", "1" | "*"] {
  if (relation === ">") return ["*", "1"];
  if (relation === "<") return ["1", "*"];
  if (relation === "<>") return ["*", "*"];
  return ["1", "1"];
}

function toReferentialAction(value?: string): DbmlReference["onDelete"] {
  const actions = [
    "cascade",
    "restrict",
    "set null",
    "set default",
    "no action",
  ] as const;
  return actions.find((action) => action === value);
}
