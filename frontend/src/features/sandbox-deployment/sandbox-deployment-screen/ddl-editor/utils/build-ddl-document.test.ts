import { describe, expect, it } from "vitest";
import { buildDdlDocument } from "./build-ddl-document";

describe("buildDdlDocument", () => {
  it("đóng gói DDL trong Markdown document", () => {
    expect(buildDdlDocument({
      title: "Sandbox",
      databaseName: "warehouse",
      ddlCode: "CREATE TABLE users (id INT);",
    })).toBe(
      "# Sandbox\n\n## warehouse\n\n```sql\nCREATE TABLE users (id INT);\n```\n",
    );
  });
});
