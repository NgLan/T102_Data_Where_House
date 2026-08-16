import { beforeEach, describe, expect, it, vi } from "vitest";
import { getProjectDetails, updateProjectDetails } from "./project-service";

const mocks = vi.hoisted(() => ({
  client: {},
  get: vi.fn(),
  update: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: mocks.client,
  getProject: mocks.get,
  updateProject: mocks.update,
}));

const project = {
  id: "project-1",
  name: "Sales",
  requirement: "Track revenue",
  user_id: "user-1",
  status: "ACTIVE" as const,
  domain: "retail",
  description: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  data_source_ids: [],
  data_sources: [],
};

describe("project details generated SDK adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("loads the project from the response envelope", async () => {
    mocks.get.mockResolvedValue({ data: { data: project } });
    await expect(getProjectDetails("project-1")).resolves.toEqual(project);
    expect(mocks.get).toHaveBeenCalledWith(expect.objectContaining({
      client: mocks.client,
      path: { project_id: "project-1" },
      responseStyle: "fields",
      throwOnError: true,
    }));
  });

  it("updates project details through the fields response style", async () => {
    mocks.update.mockResolvedValue({ data: { data: project } });
    const form = { name: "Sales", domain: "retail", requirement: "Track revenue" };
    await expect(updateProjectDetails("project-1", form)).resolves.toEqual(project);
    expect(mocks.update).toHaveBeenCalledWith(expect.objectContaining({
      body: { ...form, description: form.requirement },
      responseStyle: "fields",
    }));
  });
});
