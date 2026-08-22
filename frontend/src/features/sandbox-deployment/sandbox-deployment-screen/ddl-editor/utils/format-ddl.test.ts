import { describe, expect, it } from "vitest";
import { formatDdl } from "./format-ddl";

describe("formatDdl", () => {
  it.each(["POSTGRESQL", "SNOWFLAKE", "BIGQUERY"] as const)(
    "định dạng DDL %s bằng sql-formatter",
    (dialect) => {
      expect(formatDdl("create table users(id int);", dialect)).toContain(
        "CREATE TABLE users",
      );
    },
  );

  it("giữ chuỗi rỗng và không nuốt lỗi formatter", () => {
    expect(formatDdl("", "POSTGRESQL")).toBe("");
    expect(() => formatDdl("select 'unterminated", "POSTGRESQL")).toThrow();
  });
});
