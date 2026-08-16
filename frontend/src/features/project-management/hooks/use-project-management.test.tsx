// @vitest-environment jsdom

import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useProjectManagement } from "./use-project-management";

const mocks = vi.hoisted(() => ({
  create: vi.fn(), list: vi.fn(), remove: vi.fn(), push: vi.fn(), success: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock("@/common/hooks/use-app-notification", () => ({
  useAppNotification: () => ({ notifySuccess: mocks.success }),
}));
vi.mock("../services/project-management-api", () => ({
  requestProjectCreation: mocks.create,
  requestProjectDeletion: mocks.remove,
  requestProjects: mocks.list,
}));

const project = {
  id: "project-1", name: "Sales", requirement: "Track revenue", user_id: "user-1",
  status: "ACTIVE" as const, domain: "retail", description: null,
  created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z",
  data_source_count: 0,
};

describe("useProjectManagement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("loads initially, filters, refreshes without clearing and retries", async () => {
    mocks.list.mockResolvedValue([project]);
    const { result } = renderHook(() => useProjectManagement());
    expect(result.current.status).toBe("initial-loading");
    await waitFor(() => expect(result.current.status).toBe("ready"));
    act(() => result.current.setSearchQuery("missing"));
    expect(result.current.projects).toEqual([]);
    await act(() => result.current.refreshProjects());
    expect(result.current.totalCount).toBe(1);
  });

  it("navigates after create and removes locally only after delete succeeds", async () => {
    mocks.list.mockResolvedValue([project]);
    mocks.create.mockResolvedValue(project);
    mocks.remove.mockResolvedValue(undefined);
    const { result } = renderHook(() => useProjectManagement());
    await waitFor(() => expect(result.current.totalCount).toBe(1));
    await act(() => result.current.createProject({
      name: "Sales", domain: "retail", requirement: "Track revenue",
    }));
    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1");
    await act(() => result.current.deleteProject("project-1"));
    expect(result.current.totalCount).toBe(0);
    expect(mocks.success).toHaveBeenCalledWith("MSG_PROJECT_DELETED");
  });

  it("ignores a stale refresh response", async () => {
    const first = deferred<Array<typeof project>>();
    const second = deferred<Array<typeof project>>();
    mocks.list.mockResolvedValueOnce([project])
      .mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useProjectManagement());
    await waitFor(() => expect(result.current.status).toBe("ready"));
    let staleRequest!: Promise<void>;
    let latestRequest!: Promise<void>;
    act(() => {
      staleRequest = result.current.refreshProjects();
      latestRequest = result.current.refreshProjects();
    });
    second.resolve([{ ...project, id: "project-latest", name: "Latest" }]);
    await act(() => latestRequest);
    first.resolve([{ ...project, id: "project-stale", name: "Stale" }]);
    await act(() => staleRequest);
    expect(result.current.projects[0].name).toBe("Latest");
  });

  it("exposes an initial error and recovers through retry", async () => {
    mocks.list.mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce([project]);
    const { result } = renderHook(() => useProjectManagement());
    await waitFor(() => expect(result.current.status).toBe("error"));
    await act(() => result.current.retryProjects());
    expect(result.current.status).toBe("ready");
    expect(result.current.totalCount).toBe(1);
  });

  it("keeps the local project when delete fails", async () => {
    mocks.list.mockResolvedValue([project]);
    mocks.remove.mockRejectedValue(new Error("delete failed"));
    const { result } = renderHook(() => useProjectManagement());
    await waitFor(() => expect(result.current.totalCount).toBe(1));
    await expect(act(() => result.current.deleteProject("project-1"))).rejects.toThrow();
    expect(result.current.totalCount).toBe(1);
  });
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}
