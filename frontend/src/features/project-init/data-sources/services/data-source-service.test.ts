import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  deleteDataSource,
  listDataSources,
  updateDataSourceColumn,
  uploadDataSources,
} from "./data-source-service";

const mocks = vi.hoisted(() => ({
  client: {},
  list: vi.fn(),
  upload: vi.fn(),
  update: vi.fn(),
  remove: vi.fn(),
}));

vi.mock("@/api", () => ({
  apiClient: mocks.client,
  deleteProjectDataSource: mocks.remove,
  getProjectDataSourcePreview: vi.fn(),
  listProjectDataSources: mocks.list,
  updateProjectDataSourceColumn: mocks.update,
  uploadProjectDataSources: mocks.upload,
}));

const source = {
  id: "source-1", project_id: "project-1", name: "orders.csv",
  type: "CSV", description: null, tables: [],
};

describe("data source generated SDK adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("unwraps list payload with actor permission", async () => {
    const payload = { items: [source], can_edit: true };
    mocks.list.mockResolvedValue({ data: { data: payload } });
    await expect(listDataSources("project-1")).resolves.toEqual(payload);
    expect(mocks.list).toHaveBeenCalledWith(expect.objectContaining({
      client: mocks.client, path: { project_id: "project-1" },
      responseStyle: "fields", throwOnError: true,
    }));
  });

  it("passes files through generated multipart body", async () => {
    const file = new File(["id\n1"], "orders.csv", { type: "text/csv" });
    mocks.upload.mockResolvedValue({ data: { data: { data_sources: [source] } } });
    await uploadDataSources("project-1", [file]);
    expect(mocks.upload).toHaveBeenCalledWith(expect.objectContaining({ body: { files: [file] } }));
  });

  it("uses the dedicated column and delete paths", async () => {
    const body = {
      table_name: "orders", column_name: "status",
      data_type: "OPTION" as const, options: ["new", "done"],
    };
    mocks.update.mockResolvedValue({ data: { data: source } });
    await updateDataSourceColumn("project-1", "source-1", body);
    expect(mocks.update).toHaveBeenCalledWith(expect.objectContaining({
      body, path: { project_id: "project-1", data_source_id: "source-1" },
    }));

    mocks.remove.mockResolvedValue({ data: undefined });
    await deleteDataSource("project-1", "source-1");
    expect(mocks.remove).toHaveBeenCalledWith(expect.objectContaining({
      path: { project_id: "project-1", data_source_id: "source-1" },
    }));
  });
});
