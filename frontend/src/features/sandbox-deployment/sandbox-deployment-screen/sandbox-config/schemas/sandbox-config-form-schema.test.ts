import { describe, expect, it } from "vitest";
import {
  DEFAULT_SANDBOX_CONFIG,
  parseSandboxConfigForm,
  toSandboxConfigFormValues,
} from "./sandbox-config-form-schema";

describe("sandbox config form schema", () => {
  it("normalize form sang generated request PostgreSQL", () => {
    const result = parseSandboxConfigForm({
      ...DEFAULT_SANDBOX_CONFIG,
      host: " db.local ",
      username: " admin ",
      password: "",
      schemaName: " sandbox ",
    });
    expect(result.success && result.data).toMatchObject({
      db_type: "POSTGRESQL",
      host: "db.local",
      username: "admin",
      password: null,
      schema_name: "sandbox",
    });
  });

  it.each([
    { field: "host", values: { host: "" } },
    { field: "port", values: { port: 0 } },
    { field: "port", values: { port: 65536 } },
    { field: "schema_name", values: { schemaName: "bad schema" } },
  ])("từ chối $field không hợp lệ", ({ values }) => {
    expect(parseSandboxConfigForm({
      ...DEFAULT_SANDBOX_CONFIG,
      ...values,
    }).success).toBe(false);
  });

  it("không dựng lại password từ response", () => {
    expect(toSandboxConfigFormValues({
      id: "config-1",
      project_id: "project-1",
      db_type: "POSTGRESQL",
      host: "db.local",
      port: 5432,
      database_name: "warehouse",
      username: "admin",
      schema_name: "sandbox",
    }).password).toBe("");
  });
});
