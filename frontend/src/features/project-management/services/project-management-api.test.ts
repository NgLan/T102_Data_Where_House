import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  requestProjectCreation,
  requestProjectDeletion,
  requestProjects,
} from "./project-management-api";

const mocks = vi.hoisted(() => ({
  client: {}, create: vi.fn(), list: vi.fn(), remove: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: mocks.client,
  createProject: mocks.create,
  deleteProject: mocks.remove,
  listProjects: mocks.list,
}));

const project = {
  id: "project-1", name: "Sales", requirement: "Track revenue", user_id: "user-1",
  status: "ACTIVE" as const, domain: "retail", description: null,
  created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z",
  data_source_count: 0,
};

describe("project management generated SDK adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("passes the shared client and unwraps list data", async () => {
    mocks.list.mockResolvedValue({ data: { data: [project] } });
    await expect(requestProjects()).resolves.toEqual([project]);
    expect(mocks.list).toHaveBeenCalledWith(expect.objectContaining({
      client: mocks.client, responseStyle: "fields", throwOnError: true,
    }));
  });

  it("passes the generated create body without hidden defaults", async () => {
    mocks.create.mockResolvedValue({ data: { data: project } });
    const body = { name: "Sales", domain: "retail", requirement: "Track revenue" };
    await expect(requestProjectCreation(body)).resolves.toEqual(project);
    expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({ body }));
  });

  it("passes project_id through the generated delete path", async () => {
    mocks.remove.mockResolvedValue({ data: undefined });
    await requestProjectDeletion("project-1");
    expect(mocks.remove).toHaveBeenCalledWith(expect.objectContaining({
      client: mocks.client, path: { project_id: "project-1" },
    }));
  });
});
