import type { DbmlReference } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { RelationshipKind } from "../types/relationship-types";

/** Chuyển cardinality UI sang toán tử relationship DBML.
 * @param kind Cardinality do inspector chọn.
 * @returns Toán tử DBML tương ứng.
 */
export function relationshipKindToDbml(
  kind: RelationshipKind,
): DbmlReference["relation"] {
  if (kind === "one-to-one") return "-";
  if (kind === "one-to-many") return "<";
  return kind === "many-to-many" ? "<>" : ">";
}

/** Chuyển toán tử relationship DBML sang cardinality UI.
 * @param relation Toán tử trong canonical document.
 * @returns Cardinality dùng bởi inspector.
 */
export function dbmlToRelationshipKind(
  relation: DbmlReference["relation"],
): RelationshipKind {
  if (relation === "-") return "one-to-one";
  if (relation === "<") return "one-to-many";
  return relation === "<>" ? "many-to-many" : "many-to-one";
}
