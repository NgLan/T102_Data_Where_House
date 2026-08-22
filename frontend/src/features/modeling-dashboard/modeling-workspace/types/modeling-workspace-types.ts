import type { DataModelResponse } from "@/api";

/** Trạng thái vòng đời request của modeling workspace.
 *
 * `empty` không phải lỗi: dự án tồn tại nhưng chưa có Data Model nào được lưu, thường gặp
 * ngay sau khi khởi tạo dự án ở Bước 1. Workspace mở với mô hình trống để người dùng tự
 * dựng bảng hoặc nhờ Agent sinh, thay vì báo lỗi hệ thống.
 */
export type WorkspaceStatus =
  | "ready"
  | "empty"
  | "loading"
  | "generating"
  | "saving"
  | "saved"
  | "conflict"
  | "error";

/** Mã lỗi Backend trả về khi dự án chưa có Data Model nào. */
export const DATA_MODEL_NOT_FOUND = "DATA_MODEL_NOT_FOUND";

/** Input cấu hình cho hook generated Data Model snapshot. */
export interface DataModelSnapshotOptions {
  projectId: string | null;
  onSnapshot: (snapshot: DataModelResponse) => void;
}
