/** Tạo handle ổn định cho một cột trên graph. */
export function createColumnHandle(
  tableId: string,
  columnId: string,
  side: "source" | "target",
): string {
  return `${side}:${tableId}:${columnId}`;
}

/** Đọc table và column id từ React Flow handle. */
export function parseColumnHandle(
  value: string | null,
): { tableId: string; columnId: string } | null {
  const parts = value?.split(":");
  return parts?.length === 3 ? { tableId: parts[1], columnId: parts[2] } : null;
}
