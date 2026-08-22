"use client";

import { useState } from "react";
import type { SandboxConfigResponse } from "@/api";
import { useAppNotification } from "@/common/notifications";
import {
  SANDBOX_DB_TYPE,
  type DdlDialect,
} from "../../../constants/supported-ddl-dialects";
import { appendExecutionLogs } from "../utils/execution-log-state";
import type { ExecutionLogState } from "../utils/execution-log-state";
import { useSandboxExecutionMutation } from "./use-sandbox-execution-mutation";

interface SandboxExecutionInput {
  projectId: string;
  ddlCode: string;
  dialect: DdlDialect;
  savedConfig: SandboxConfigResponse | null;
}

/** Quản lý reset policy và điều phối Sandbox execution. */
export function useSandboxExecution(input: SandboxExecutionInput) {
  const { notifyError, notifyWarning } = useAppNotification();
  const [shouldResetSchema, setShouldResetSchema] = useState(true);
  const [logState, setLogState] = useState<ExecutionLogState>({
    projectId: input.projectId,
    entries: [],
  });
  const schemaName = input.savedConfig?.schema_name ?? "public";
  const isSchemaProtected = schemaName.trim().toLowerCase() === "public";
  const mutation = useSandboxExecutionMutation({
    ...input,
    shouldResetSchema: shouldResetSchema && !isSchemaProtected,
    onAppendLogs: (logs) =>
      appendExecutionLogs(setLogState, input.projectId, logs),
  });
  const execute = () => {
    if (!input.savedConfig) return notifyError("SANDBOX_CONFIG_NOT_FOUND");
    if (!input.ddlCode.trim()) return notifyWarning("MSG_DDL_REQUIRED");
    if (input.dialect !== SANDBOX_DB_TYPE) {
      return notifyError("UNSUPPORTED_SANDBOX_DB_TYPE");
    }
    mutation.mutate();
  };
  return {
    execute,
    isExecuting: mutation.isPending,
    isSchemaProtected,
    logs: logState.projectId === input.projectId ? logState.entries : [],
    schemaName,
    shouldResetSchema,
    setShouldResetSchema,
  };
}
