import { beforeEach, describe, expect, it, vi } from "vitest";
import { deleteDataSource, listDataSources, uploadDataSources } from "./data-sources-api";

const mocks = vi.hoisted(() => ({ client: {}, list: vi.fn(), upload: vi.fn(), remove: vi.fn() }));
vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()), apiClient: mocks.client,
  deleteProjectDataSource: mocks.remove, getProjectDataSourcePreview: vi.fn(),
  listProjectDataSources: mocks.list, uploadProjectDataSources: mocks.upload,
}));
const source = { id: "source-1", project_id: "project-1", name: "orders.csv",
  type: "CSV", description: null, tables: [], analysis_status: "PENDING" };

describe("data source generated SDK adapter", () => {
  beforeEach(() => vi.clearAllMocks());
  it("unwraps list payload with actor permission", async () => {
    const payload = { items: [source], can_edit: true };
    mocks.list.mockResolvedValue({ data: { data: payload } });
    await expect(listDataSources("project-1")).resolves.toEqual(payload);
  });
  it("passes files through generated multipart body", async () => {
    const file = new File(["id\n1"], "orders.csv", { type: "text/csv" });
    mocks.upload.mockResolvedValue({ data: { data: { data_sources: [source], total_files_uploaded: 1 } } });
    await uploadDataSources("project-1", [file]);
    expect(mocks.upload).toHaveBeenCalledWith(expect.objectContaining({ body: { files: [file] } }));
  });
  it("uses the dedicated delete path", async () => {
    mocks.remove.mockResolvedValue({ data: undefined });
    await deleteDataSource("project-1", "source-1");
    expect(mocks.remove).toHaveBeenCalledWith(expect.objectContaining({
      path: { project_id: "project-1", source_id: "source-1" },
    }));
  });
});
