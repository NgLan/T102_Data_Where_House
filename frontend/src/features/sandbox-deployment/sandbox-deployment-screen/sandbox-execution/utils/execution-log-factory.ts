import type { ExecuteDdlResponse, SandboxConfigResponse } from "@/api";
import type {
  ExecutionLogEntry,
  ExecutionLogType,
  SandboxTranslationKey,
} from "../types/execution-log-types";

let localLogSequence = 0;

/** Tạo log bắt đầu execution bằng thông tin config đã lưu. */
export function createExecutionStartLog(
  config: SandboxConfigResponse | null,
): ExecutionLogEntry {
  return createTranslatedLog("MSG_LOG_EXECUTING", "info", {
    host: config?.host ?? "",
    port: config?.port ?? "",
    databaseName: config?.database_name ?? "",
  });
}

/** Tạo log tổng kết response execution. */
export function createExecutionSummaryLog(
  response: ExecuteDdlResponse,
): ExecutionLogEntry {
  return createTranslatedLog(
    "MSG_EXECUTION_SUMMARY",
    response.success ? "success" : "error",
    {
      succeeded: response.succeeded_statements,
      executed: response.executed_statements,
      duration: response.total_duration_ms,
    },
  );
}

/** Tạo log lỗi tham chiếu tới errors namespace. */
export function createExecutionErrorLog(errorCode: string): ExecutionLogEntry {
  return { ...createLogBase("error"), errorCode };
}

function createTranslatedLog(
  translationKey: SandboxTranslationKey,
  type: ExecutionLogType,
  params: Record<string, string | number>,
): ExecutionLogEntry {
  return { ...createLogBase(type), translationKey, params };
}

function createLogBase(type: ExecutionLogType) {
  localLogSequence += 1;
  return {
    id: `local-${Date.now()}-${localLogSequence}`,
    timestamp: new Date().toLocaleTimeString(),
    type,
  };
}
