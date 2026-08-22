import type { StatementLogResponse } from "@/api";
import type { ExecutionLogEntry } from "../types/execution-log-types";

/** Ánh xạ statement logs của API thành view model có key ổn định. */
export function mapStatementLogs(
  logs: readonly StatementLogResponse[],
): ExecutionLogEntry[] {
  return logs.map((log, index) => ({
    id: `statement-${log.timestamp}-${index}-${log.statement}`,
    timestamp: log.timestamp,
    type: log.is_success ? "success" : "error",
    translationKey: log.is_success
      ? "MSG_STATEMENT_SUCCEEDED"
      : "MSG_STATEMENT_FAILED",
    params: {
      duration: log.execution_time_ms,
      statement: log.statement.split("\n")[0],
      errorDetail: log.error_detail ?? "",
    },
  }));
}
