import { describe, expect, it } from "vitest";
import type { DataSourceResponse } from "@/api";
import { validateSourceFiles } from "./data-source-upload-validation";

const source = (name: string): DataSourceResponse => ({ id: name, project_id: "project-1", name,
  type: "CSV", description: null, tables: [], analysis_status: "PENDING" });

describe("validateSourceFiles", () => {
  it("allows case-insensitive replacement when all slots are used", () => {
    const sources = Array.from({ length: 19 }, (_, index) => source(`${index}.csv`));
    sources.push(source("orders.csv"));
    expect(validateSourceFiles([new File(["id"], "ORDERS.CSV")], sources)).toBeNull();
  });
  it("rejects a new source above the total limit", () => {
    const sources = Array.from({ length: 20 }, (_, index) => source(`${index}.csv`));
    expect(validateSourceFiles([new File(["id"], "extra.csv")], sources)).toBe("MAX_FILES_EXCEEDED");
  });
});
