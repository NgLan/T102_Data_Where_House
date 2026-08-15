import type { DataModelResponse } from "@/api";

/** Trạng thái vòng đời request của modeling workspace. */
export type WorkspaceStatus =
  | "ready"
  | "loading"
  | "saving"
  | "saved"
  | "conflict"
  | "error";

/** Input cấu hình cho hook generated Data Model snapshot. */
export interface DataModelSnapshotOptions {
  projectId: string | null;
  onSnapshot: (snapshot: DataModelResponse) => void;
}
