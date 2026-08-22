import {
  getSandboxConfig as requestSandboxConfig,
  requireApiData,
  saveSandboxConfig as requestSaveSandboxConfig,
  testSandboxConnection as requestSandboxConnectionTest,
  unwrapApiData,
  type SandboxConfigRequest,
  type SandboxConfigResponse,
  type TestConnectionResponse,
} from "@/api";
import { createSandboxRequestOptions } from "../../services/sandbox-api-request-options";

/** Lấy cấu hình Sandbox mà không làm lộ password đã lưu. */
export async function getSandboxConfig(
  projectId: string,
): Promise<SandboxConfigResponse | null> {
  const response = await requestSandboxConfig(
    createSandboxRequestOptions(projectId, false),
  );
  return unwrapApiData(response.data);
}

/** Lưu cấu hình Sandbox; password null/rỗng giữ credential cũ ở Backend. */
export async function saveSandboxConfig(
  projectId: string,
  request: SandboxConfigRequest,
): Promise<SandboxConfigResponse> {
  const response = await requestSaveSandboxConfig({
    ...createSandboxRequestOptions(projectId),
    body: request,
  });
  return requireApiData(response.data);
}

/** Kiểm tra kết nối bằng chính credential đang có trên form. */
export async function testSandboxConnection(
  projectId: string,
  request: SandboxConfigRequest,
): Promise<TestConnectionResponse> {
  const response = await requestSandboxConnectionTest({
    ...createSandboxRequestOptions(projectId),
    body: request,
  });
  return requireApiData(response.data);
}
