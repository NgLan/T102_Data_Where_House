import { describe, expect, it, vi } from "vitest";
import { executeSandboxDdl } from "./sandbox-execution-api";

const mocks = vi.hoisted(() => ({ client: {}, execute: vi.fn() }));
vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: mocks.client,
  executeSandboxDdl: mocks.execute,
}));

describe("executeSandboxDdl", () => {
  it("map input sang generated request body", async () => {
    const response = {
      success: true,
      executed_statements: 1,
      succeeded_statements: 1,
      failed_statements: 0,
      total_duration_ms: 3,
      logs: [],
    };
    mocks.execute.mockResolvedValue({ data: { data: response } });
    await expect(executeSandboxDdl({
      projectId: "project-1",
      ddlScript: "CREATE TABLE users;",
      shouldResetSchema: false,
    })).resolves.toBe(response);
    expect(mocks.execute).toHaveBeenCalledWith(expect.objectContaining({
      path: { project_id: "project-1" },
      body: { ddl_script: "CREATE TABLE users;", reset_schema: false },
    }));
  });
});
