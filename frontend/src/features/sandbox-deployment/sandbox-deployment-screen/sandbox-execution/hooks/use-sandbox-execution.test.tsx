// @vitest-environment jsdom

import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { SandboxConfigResponse } from "@/api";
import { useSandboxExecution } from "./use-sandbox-execution";
import { useSandboxExecutionMutation } from "./use-sandbox-execution-mutation";

const mocks = vi.hoisted(() => ({
  mutate: vi.fn(),
  notifyError: vi.fn(),
  notifyWarning: vi.fn(),
}));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => ({
    notifyError: mocks.notifyError,
    notifyWarning: mocks.notifyWarning,
  }),
}));
vi.mock("./use-sandbox-execution-mutation", () => ({
  useSandboxExecutionMutation: vi.fn(() => ({
    isPending: false,
    mutate: mocks.mutate,
  })),
}));

const config = {
  id: "config-1",
  project_id: "project-1",
  db_type: "POSTGRESQL",
  host: "localhost",
  port: 5432,
  database_name: "sandbox_db",
  schema_name: " PUBLIC ",
} as SandboxConfigResponse;

describe("useSandboxExecution", () => {
  beforeEach(() => vi.clearAllMocks());

  it("normalize public schema và không gửi reset destructive", () => {
    const { result } = renderHook(() => useSandboxExecution({
      projectId: "project-1",
      ddlCode: "CREATE TABLE users;",
      dialect: "POSTGRESQL",
      savedConfig: config,
    }));
    expect(result.current.isSchemaProtected).toBe(true);
    expect(vi.mocked(useSandboxExecutionMutation)).toHaveBeenCalledWith(
      expect.objectContaining({ shouldResetSchema: false }),
    );
    act(() => result.current.execute());
    expect(mocks.mutate).toHaveBeenCalledOnce();
  });

  it("chặn dialect không thể execute trước API", () => {
    const { result } = renderHook(() => useSandboxExecution({
      projectId: "project-1",
      ddlCode: "CREATE TABLE users;",
      dialect: "SNOWFLAKE",
      savedConfig: config,
    }));
    act(() => result.current.execute());
    expect(mocks.notifyError).toHaveBeenCalledWith("UNSUPPORTED_SANDBOX_DB_TYPE");
    expect(mocks.mutate).not.toHaveBeenCalled();
  });
});
