import type { DataModelValidationIssueResponse } from "@/api";

/** Nhóm issue theo tên bảng không phân biệt hoa thường. */
export function groupValidationIssues(
  issues: DataModelValidationIssueResponse[],
): Map<string, DataModelValidationIssueResponse[]> {
  const grouped = new Map<string, DataModelValidationIssueResponse[]>();
  for (const issue of issues) {
    if (!issue.table_name) continue;
    const key = issue.table_name.toLocaleLowerCase();
    grouped.set(key, [...(grouped.get(key) ?? []), issue]);
  }
  return grouped;
}

/** Trả issue không có vị trí bảng để hiển thị ở summary chung. */
export function getGlobalValidationIssues(
  issues: DataModelValidationIssueResponse[],
): DataModelValidationIssueResponse[] {
  return issues.filter((issue) => !issue.table_name);
}
