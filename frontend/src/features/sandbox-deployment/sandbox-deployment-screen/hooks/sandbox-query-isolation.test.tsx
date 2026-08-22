// @vitest-environment jsdom

import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useDdlEditor } from "../ddl-editor/hooks/use-ddl-editor";
import { generateDataModelDdl } from "../ddl-editor/services/data-model-ddl-api";
import { useSandboxConfig } from "../sandbox-config/hooks/use-sandbox-config";
import { getSandboxConfig } from "../sandbox-config/services/sandbox-config-api";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => ({
    notifyError: vi.fn(),
    notifySuccess: vi.fn(),
    notifyWarning: vi.fn(),
  }),
}));
vi.mock("../ddl-editor/services/data-model-ddl-api", () => ({
  generateDataModelDdl: vi.fn(),
}));
vi.mock("../sandbox-config/services/sandbox-config-api", () => ({
  getSandboxConfig: vi.fn(),
  saveSandboxConfig: vi.fn(),
  testSandboxConnection: vi.fn(),
}));

describe("sandbox query isolation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getSandboxConfig).mockResolvedValue(null);
    vi.mocked(generateDataModelDdl).mockImplementation(async (_, dialect) => ({
      ddl: `DDL ${dialect}`,
      db_type: dialect,
      data_model_id: "model-1",
      data_model_revision: 1,
    }));
  });

  it("đổi DDL dialect không refetch Sandbox config", async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => ({
      config: useSandboxConfig("project-1"),
      editor: useDdlEditor("project-1", "sandbox_db"),
    }), { wrapper });
    await waitFor(() => expect(result.current.editor.ddlCode).toBe("DDL POSTGRESQL"));
    act(() => result.current.editor.setDialect("SNOWFLAKE"));
    await waitFor(() => expect(result.current.editor.ddlCode).toBe("DDL SNOWFLAKE"));
    expect(getSandboxConfig).toHaveBeenCalledOnce();
    expect(generateDataModelDdl).toHaveBeenCalledTimes(2);
  });
});
