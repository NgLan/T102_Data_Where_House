import { isApiError } from "@/api";

export type ProjectInitPhase =
  | "IDLE" | "SAVING_DRAFT" | "ANALYZING_REQUIREMENTS"
  | "WAITING_FOR_CLARIFICATION" | "ANALYZING_SOURCE"
  | "RECHECKING_SOURCE"
  | "GENERATING_DATA_MODEL" | "SOURCE_CONFIRMATION_REQUIRED"
  | "SOURCE_DATA_REQUIRED" | "FAILED";

export function readinessPhase(status: string): ProjectInitPhase | null {
  if (status === "SOURCE_CONFIRMATION_REQUIRED") return "SOURCE_CONFIRMATION_REQUIRED";
  if (status === "SOURCE_DATA_REQUIRED") return "SOURCE_DATA_REQUIRED";
  if (status === "REQUIREMENT_CLARIFICATION_REQUIRED") return "WAITING_FOR_CLARIFICATION";
  return null;
}

export function shouldPause(state: {
  status: string;
  continuation_state: string;
}): boolean {
  return state.status === "NEEDS_CLARIFICATION" || state.status === "PROCESSING" ||
    state.continuation_state === "AWAITING_DECISION";
}

export function handleWorkflowError(
  error: unknown,
  setPhase: (phase: ProjectInitPhase) => void,
  notifyError: (code?: string) => void,
) {
  setPhase("FAILED");
  notifyError(isApiError(error) ? error.errorCode : undefined);
}
