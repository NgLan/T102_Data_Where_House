import { apiClient } from "@/api";

/** Tạo phần request options dùng chung cho mọi Sandbox operation. */
export function createSandboxRequestOptions(
  projectId: string,
  shouldNotify = true,
) {
  return {
    client: apiClient,
    path: { project_id: projectId },
    responseStyle: "fields" as const,
    throwOnError: true as const,
    meta: { shouldNotify },
  };
}
