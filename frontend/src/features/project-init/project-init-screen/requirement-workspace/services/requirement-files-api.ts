import type {
  RequirementFileListResponse,
  UploadRequirementFilesResponse,
} from "@/api";
import {
  apiClient,
  deleteProjectRequirementFile,
  listProjectRequirementFiles,
  requireApiData,
  uploadProjectRequirementFiles,
} from "@/api";

/** Đọc metadata documents; backend không expose extracted text/location. */
export async function requestRequirementFiles(
  projectId: string,
): Promise<RequirementFileListResponse> {
  const response = await listProjectRequirementFiles({
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Upload/replace batch documents tại expected shared revision. */
export async function requestRequirementFileUpload(
  projectId: string,
  files: File[],
  expectedRevision: number,
): Promise<UploadRequirementFilesResponse> {
  const response = await uploadProjectRequirementFiles({
    body: { files, expected_revision: expectedRevision },
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

/** Xóa một document bằng optimistic revision. */
export async function requestRequirementFileDelete(
  projectId: string,
  fileId: string,
  expectedRevision: number,
): Promise<void> {
  await deleteProjectRequirementFile({
    client: apiClient,
    path: { project_id: projectId, file_id: fileId },
    query: { expected_revision: expectedRevision },
    responseStyle: "fields",
    throwOnError: true,
  });
}
