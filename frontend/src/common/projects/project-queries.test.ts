import { QueryClient } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { accessibleProjectsQueryOptions, PROJECTS_QUERY_KEY } from "./project-queries";
import { getAccessibleProjects } from "./project-api";

vi.mock("./project-api", () => ({
  getAccessibleProjects: vi.fn().mockResolvedValue([{ id: "project-1" }]),
  getCurrentActorProfile: vi.fn(),
}));

describe("project query cache", () => {
  beforeEach(() => vi.mocked(getAccessibleProjects).mockClear());

  it("dùng một query key/cache cho header và project list", async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000 } } });
    const first = await queryClient.fetchQuery(accessibleProjectsQueryOptions());
    const second = await queryClient.fetchQuery(accessibleProjectsQueryOptions());
    expect(first).toBe(second);
    expect(getAccessibleProjects).toHaveBeenCalledTimes(1);
    expect(accessibleProjectsQueryOptions().queryKey).toEqual(PROJECTS_QUERY_KEY);
  });
});
