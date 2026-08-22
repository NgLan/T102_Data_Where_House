import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  getSandboxConfig,
  saveSandboxConfig,
  testSandboxConnection,
} from "./sandbox-config-api";

const mocks = vi.hoisted(() => ({
  client: {},
  get: vi.fn(),
  save: vi.fn(),
  test: vi.fn(),
}));
vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: mocks.client,
  getSandboxConfig: mocks.get,
  saveSandboxConfig: mocks.save,
  testSandboxConnection: mocks.test,
}));

const request = {
  db_type: "POSTGRESQL" as const,
  host: "localhost",
  port: 5432,
  database_name: "sandbox_db",
};

describe("sandbox config API", () => {
  beforeEach(() => vi.clearAllMocks());

  it("trả null khi project chưa có config", async () => {
    mocks.get.mockResolvedValue({ data: { data: null } });
    await expect(getSandboxConfig("project-1")).resolves.toBeNull();
    expect(mocks.get).toHaveBeenCalledWith(expect.objectContaining({
      path: { project_id: "project-1" },
      meta: { shouldNotify: false },
    }));
  });

  it("gửi generated body khi lưu config", async () => {
    const config = { id: "config-1", host: "localhost" };
    mocks.save.mockResolvedValue({ data: { data: config } });
    await expect(saveSandboxConfig("project-1", request)).resolves.toBe(config);
    expect(mocks.save).toHaveBeenCalledWith(expect.objectContaining({ body: request }));
  });

  it("gửi credential hiện tại khi test connection", async () => {
    const response = { success: true, message: "ok", latency_ms: 4 };
    mocks.test.mockResolvedValue({ data: { data: response } });
    await expect(testSandboxConnection("project-1", request)).resolves.toBe(response);
    expect(mocks.test).toHaveBeenCalledWith(expect.objectContaining({ body: request }));
  });
});
