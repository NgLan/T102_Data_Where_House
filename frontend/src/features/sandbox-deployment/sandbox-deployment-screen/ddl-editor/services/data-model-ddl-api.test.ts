import { describe, expect, it, vi } from "vitest";
import { generateDataModelDdl } from "./data-model-ddl-api";

const mocks = vi.hoisted(() => ({ client: {}, generate: vi.fn() }));
vi.mock("@/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api")>()),
  apiClient: mocks.client,
  generateDataModelDdl: mocks.generate,
}));

describe("generateDataModelDdl", () => {
  it("gửi project path và dialect qua generated operation", async () => {
    const ddl = { ddl: "CREATE TABLE users;", db_type: "SNOWFLAKE" };
    mocks.generate.mockResolvedValue({ data: { data: ddl } });
    await expect(generateDataModelDdl("project-1", "SNOWFLAKE")).resolves.toBe(ddl);
    expect(mocks.generate).toHaveBeenCalledWith(expect.objectContaining({
      client: mocks.client,
      path: { project_id: "project-1" },
      query: { db_type: "SNOWFLAKE" },
      meta: { shouldNotify: false },
      throwOnError: true,
    }));
  });
});
