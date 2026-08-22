// @vitest-environment jsdom

import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectSummaryResponse } from "@/api";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { deleteProject } from "../services/project-mutations-api";
import { useDeleteProject } from "./use-delete-project";

const mocks = vi.hoisted(() => ({ notifyError: vi.fn(), notifySuccess: vi.fn() }));
vi.mock("../services/project-mutations-api", () => ({ deleteProject: vi.fn() }));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => mocks,
}));

function project(id: string): ProjectSummaryResponse {
  return {
    id, name: id, user_id: "user", status: "ACTIVE", domain: null, description: null,
    created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z",
    data_source_count: 0, is_data_model_outdated: false,
  };
}

describe("useDeleteProject", () => {
  beforeEach(() => vi.clearAllMocks());

  it("theo dõi nhiều project đang xóa và cập nhật shared cache", async () => {
    const resolvers = new Map<string, () => void>();
    vi.mocked(deleteProject).mockImplementation((id) => new Promise<void>((resolve) => {
      resolvers.set(id, resolve);
    }));
    const queryClient = new QueryClient();
    queryClient.setQueryData(PROJECTS_QUERY_KEY, [project("one"), project("two")]);
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(useDeleteProject, { wrapper });
    act(() => {
      void result.current.deleteProject("one");
      void result.current.deleteProject("two");
    });
    await waitFor(() => expect([...result.current.deletingProjectIds].sort())
      .toEqual(["one", "two"]));
    act(() => resolvers.get("one")?.());
    await waitFor(() => expect(result.current.deletingProjectIds.has("one")).toBe(false));
    expect(queryClient.getQueryData<ProjectSummaryResponse[]>(PROJECTS_QUERY_KEY)
      ?.map(({ id }) => id)).toEqual(["two"]);
    act(() => resolvers.get("two")?.());
    await waitFor(() => expect(result.current.deletingProjectIds.size).toBe(0));
  });
});
