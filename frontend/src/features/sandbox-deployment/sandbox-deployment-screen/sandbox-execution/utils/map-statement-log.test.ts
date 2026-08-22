import { describe, expect, it } from "vitest";
import { mapStatementLogs } from "./map-statement-log";

describe("mapStatementLogs", () => {
  it("giữ duration, statement và error detail bằng translation params", () => {
    const result = mapStatementLogs([
      { statement: "CREATE TABLE users (\n id INT\n);", is_success: true, execution_time_ms: 8, timestamp: "10:00" },
      { statement: "DROP TABLE missing;", is_success: false, execution_time_ms: 2, timestamp: "10:01", error_detail: "not found" },
    ]);
    expect(result[0]).toMatchObject({
      type: "success",
      translationKey: "MSG_STATEMENT_SUCCEEDED",
      params: { duration: 8, statement: "CREATE TABLE users (" },
    });
    expect(result[1]).toMatchObject({
      type: "error",
      translationKey: "MSG_STATEMENT_FAILED",
      params: { errorDetail: "not found" },
    });
    expect(result[0].id).not.toBe(result[1].id);
  });
});
