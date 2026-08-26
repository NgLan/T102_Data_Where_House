import type { UseFormSetError } from "react-hook-form";
import type { ApiError } from "@/api";
import { CUSTOM_PROJECT_DOMAIN } from "@/common/projects/project-domain-options";
import type { CreateProjectFormValues } from "../schemas/create-project-form-schema";

/** Ánh xạ validation detail của Project API vào field đang hiển thị.
 * @param error ApiError có danh sách field details.
 * @param setError Setter của React Hook Form.
 * @param domainSelection Lựa chọn domain hiện tại để định tuyến lỗi custom.
 * @returns Số detail không thể hiển thị inline.
 */
export function mapProjectApiFieldErrors(
  error: ApiError,
  setError: UseFormSetError<CreateProjectFormValues>,
  domainSelection: string,
): number {
  let unmappedCount = 0;
  for (const detail of error.details) {
    if (!("field" in detail)) {
      unmappedCount += 1;
      continue;
    }
    const field = resolveProjectField(detail.field, domainSelection);
    if (!field) {
      unmappedCount += 1;
      continue;
    }
    setError(field, { type: "server", message: detail.message });
  }
  return unmappedCount;
}

function resolveProjectField(
  path: string,
  domainSelection: string,
): keyof CreateProjectFormValues | null {
  const field = path.split(".").at(-1);
  if (field === "domain") {
    return domainSelection === CUSTOM_PROJECT_DOMAIN ? "customDomain" : "domainSelection";
  }
  return field === "name" || field === "description" ? field : null;
}
