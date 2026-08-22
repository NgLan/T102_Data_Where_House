import type { Dispatch, SetStateAction } from "react";
import type { ExecutionLogEntry } from "../types/execution-log-types";

export interface ExecutionLogState {
  projectId: string;
  entries: ExecutionLogEntry[];
}

/** Nối log và tự bỏ entries thuộc project trước đó. */
export function appendExecutionLogs(
  setState: Dispatch<SetStateAction<ExecutionLogState>>,
  projectId: string,
  logs: ExecutionLogEntry[],
): void {
  setState((current) => ({
    projectId,
    entries: [
      ...(current.projectId === projectId ? current.entries : []),
      ...logs,
    ],
  }));
}
