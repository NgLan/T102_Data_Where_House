// @vitest-environment jsdom

import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createProject } from "../services/project-mutations-api";
import { useCreateProject } from "./use-create-project";

const mocks = vi.hoisted(() => ({ push: vi.fn(), notifySuccess: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock("../services/project-mutations-api", () => ({ createProject: vi.fn() }));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => ({ notifySuccess: mocks.notifySuccess }),
}));

describe("useCreateProject", () => {
  beforeEach(() => vi.clearAllMocks());

  it("đóng dialog và mở workspace mặc định sau khi tạo", async () => {
    vi.mocked(createProject).mockResolvedValue({ id: "new-project" } as never);
    const queryClient = new QueryClient();
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    const onCreated = vi.fn();
    const { result } = renderHook(() => useCreateProject({ onCreated }), { wrapper });
    await act(() => result.current.mutateAsync({
      name: "New project", domain: "ride", description: null,
    }));
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/projects/new-project"));
    expect(onCreated).toHaveBeenCalledOnce();
    expect(mocks.notifySuccess).toHaveBeenCalledWith("MSG_PROJECT_CREATED");
  });
});
