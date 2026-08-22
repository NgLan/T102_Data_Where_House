import { dbmlDocumentSchema } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/schema";
import type { DbmlDocument } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";

import type { DataModelValidationErrors } from "../types/data-model-validation-types";
import { validateReference } from "./reference-validation";

/**
 * Thu thập lỗi Zod và lỗi endpoint relationship theo đường dẫn field.
 *
 * @param document Data Model draft cần kiểm tra.
 * @returns Map đường dẫn field sang translation key.
 */
export function validateDataModel(
  document: DbmlDocument,
): DataModelValidationErrors {
  const result = dbmlDocumentSchema.safeParse(document);
  const errors = result.success
    ? {}
    : Object.fromEntries(
        result.error.issues.map((issue) => [
          issue.path.join("."),
          issue.message,
        ]),
      );
  document.references.forEach((reference, index) =>
    validateReference({ document, reference, index, errors }),
  );
  return errors;
}
