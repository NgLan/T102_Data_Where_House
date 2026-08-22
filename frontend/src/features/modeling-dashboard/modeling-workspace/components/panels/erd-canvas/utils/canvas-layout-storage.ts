import type { StoredCanvasLayout } from "../types/erd-canvas-types";

const STORAGE_PREFIX = "uc5.1.3:erd-layout:v1:";
const EMPTY_VIEWPORT = { x: 0, y: 0, zoom: 1 };

/** Đọc layout ERD đã lưu cho một project.
 * @param projectId Định danh project hoặc `draft` khi chưa có project.
 * @returns Layout hợp lệ; trả về null khi thiếu, lỗi hoặc sai phiên bản.
 */
export function loadCanvasLayout(projectId: string): StoredCanvasLayout | null {
  if (typeof window === "undefined") return null;
  try {
    const value: unknown = JSON.parse(
      window.localStorage.getItem(storageKey(projectId)) ?? "null",
    );
    return isStoredCanvasLayout(value) ? value : null;
  } catch {
    return null;
  }
}

/** Lưu layout ERD theo project.
 * @param projectId Định danh project hoặc `draft`.
 * @param layout Vị trí node và viewport hiện tại.
 * @returns Không trả về giá trị.
 * @remarks Lỗi quota/quyền localStorage được bỏ qua để không chặn editor.
 */
export function saveCanvasLayout(
  projectId: string,
  layout: StoredCanvasLayout,
): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(storageKey(projectId), JSON.stringify(layout));
  } catch {
    // localStorage chỉ là bộ nhớ tối ưu trải nghiệm, không phải nguồn dữ liệu nghiệp vụ.
  }
}

/** Loại vị trí của bảng đã xóa và bổ sung vị trí mặc định cho bảng mới.
 * @param layout Layout đã lưu, có thể chưa tồn tại.
 * @param tableIds Các bảng hiện còn trong document.
 * @returns Layout chỉ chứa các bảng hiện hữu.
 */
export function reconcileCanvasLayout(
  layout: StoredCanvasLayout | null,
  tableIds: string[],
): StoredCanvasLayout {
  const positions = Object.fromEntries(
    tableIds.flatMap((id) => {
      const position = layout?.positions[id];
      return position ? [[id, position]] : [];
    }),
  );
  return {
    version: 1,
    positions,
    viewport: layout?.viewport ?? EMPTY_VIEWPORT,
  };
}

function storageKey(projectId: string): string {
  return `${STORAGE_PREFIX}${projectId || "draft"}`;
}

function isStoredCanvasLayout(value: unknown): value is StoredCanvasLayout {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<StoredCanvasLayout>;
  return (
    candidate.version === 1 &&
    isPointRecord(candidate.positions) &&
    isViewport(candidate.viewport)
  );
}

function isPointRecord(
  value: unknown,
): value is StoredCanvasLayout["positions"] {
  if (!value || typeof value !== "object") return false;
  return Object.values(value).every((point) => isPoint(point));
}

function isPoint(value: unknown): value is { x: number; y: number } {
  if (!value || typeof value !== "object") return false;
  const point = value as { x?: unknown; y?: unknown };
  return typeof point.x === "number" && typeof point.y === "number";
}

function isViewport(value: unknown): value is StoredCanvasLayout["viewport"] {
  if (!isPoint(value)) return false;
  return typeof (value as { zoom?: unknown }).zoom === "number";
}
