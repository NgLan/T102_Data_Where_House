"use client";

import { useMutation } from "@tanstack/react-query";
import { isApiError, type SandboxConfigResponse } from "@/api";
import { useAppNotification } from "@/common/notifications";
import { executeSandboxDdl } from "../services/sandbox-execution-api";
import type { ExecutionLogEntry } from "../types/execution-log-types";
import {
  createExecutionErrorLog,
  createExecutionStartLog,
  createExecutionSummaryLog,
} from "../utils/execution-log-factory";
import { mapStatementLogs } from "../utils/map-statement-log";

interface ExecutionMutationInput {
  projectId: string;
  ddlCode: string;
  savedConfig: SandboxConfigResponse | null;
  shouldResetSchema: boolean;
  onAppendLogs: (logs: ExecutionLogEntry[]) => void;
}

/** Gọi execute API và chuyển mọi kết quả thành notification cùng execution log. */
export function useSandboxExecutionMutation(input: ExecutionMutationInput) {
  const { notifyError, notifySuccess } = useAppNotification();
  return useMutation({
    mutationFn: () => executeSandboxDdl({
      projectId: input.projectId,
      ddlScript: input.ddlCode,
      shouldResetSchema: input.shouldResetSchema,
    }),
    onMutate: () => input.onAppendLogs([
      createExecutionStartLog(input.savedConfig),
    ]),
    onSuccess: (response) => {
      input.onAppendLogs([
        ...mapStatementLogs(response.logs),
        createExecutionSummaryLog(response),
      ]);
      if (response.success) notifySuccess("MSG_SANDBOX_EXECUTION_SUCCESS");
      else notifyError("SANDBOX_EXECUTION_ERROR");
    },
    onError: (error) => {
      const errorCode = isApiError(error) ? error.errorCode : "UNKNOWN_ERROR";
      input.onAppendLogs([createExecutionErrorLog(errorCode)]);
      if (isApiError(error) && error.kind === "validation") {
        notifyError(errorCode);
      }
    },
  });
}
