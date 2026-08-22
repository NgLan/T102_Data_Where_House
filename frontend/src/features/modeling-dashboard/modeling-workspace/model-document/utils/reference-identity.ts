import type { DbmlDocument, DbmlReference } from "../dbml/types";

export function hasDuplicateReference(
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
