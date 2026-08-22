import { describe, expect, it } from "vitest";
import type { DataSourceResponse } from "@/api";
import { validateCsvFiles } from "./data-source-upload-validation";

const source = (name: string): DataSourceResponse => ({ id: name, project_id: "project-1", name,
  type: "CSV", description: null, tables: [], analysis_status: "PENDING" });

describe("validateCsvFiles", () => {
  it("allows case-insensitive replacement when all slots are used", () => {
    const sources = Array.from({ length: 19 }, (_, index) => source(`${index}.csv`));
    sources.push(source("orders.csv"));
    expect(validateCsvFiles([new File(["id"], "ORDERS.CSV")], sources)).toBeNull();
  });
  it("rejects a new source above the total limit", () => {
    const sources = Array.from({ length: 20 }, (_, index) => source(`${index}.csv`));
    expect(validateCsvFiles([new File(["id"], "extra.csv")], sources)).toBe("MAX_FILES_EXCEEDED");
  });
});
