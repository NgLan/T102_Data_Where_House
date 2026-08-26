import { isApiError, type AnalysisStatusResponse } from "@/api";
import type { useProjectDetails } from "../project-details/hooks/use-project-details";
import type { useRequirementClarification } from "../requirement-workspace/hooks/use-requirement-clarification";
import type { useProjectAnalysis } from "./use-project-analysis";
import {
  handleWorkflowError,
  type ProjectInitPhase,
  readinessPhase,
  shouldPause,
} from "./project-init-workflow-helpers";

export interface WorkflowDependencies {
  projectId: string;
  project: ReturnType<typeof useProjectDetails>;
  clarification: ReturnType<typeof useRequirementClarification>;
  analysis: ReturnType<typeof useProjectAnalysis>;
  onOpenChat: () => void;
  onCloseChat: () => void;
}

export interface WorkflowRuntime {
  deps: WorkflowDependencies;
  setPhase: (phase: ProjectInitPhase) => void;
  notifyError: (code?: string) => void;
  notifyWarning: (key: "MSG_SOURCE_COVERAGE_BLOCKED") => void;
  onReady: () => void;
}

export async function continueWhenReady(
  runtime: WorkflowRuntime,
  current: AnalysisStatusResponse,
): Promise<void> {
  const blockedPhase = readinessPhase(current.readiness_status);
  if (blockedPhase) {
    runtime.setPhase(blockedPhase);
    runtime.notifyWarning("MSG_SOURCE_COVERAGE_BLOCKED");
    return;
  }
  runtime.setPhase("GENERATING_DATA_MODEL");
  const result = await runtime.deps.analysis.initialize();
  if (result.status === "PAUSED") {
    runtime.setPhase(readinessPhase(result.readiness_status) ?? "FAILED");
    return;
  }
  runtime.setPhase("IDLE");
  runtime.onReady();
}

export async function runWorkflow(runtime: WorkflowRuntime): Promise<void> {
  try {
    runtime.setPhase("SAVING_DRAFT");
    if (!(await runtime.deps.project.saveInputsForWorkflow())) {
      return runtime.setPhase("FAILED");
    }
    let state = (await runtime.deps.clarification.stateQuery.refetch()).data;
    if (!state) return runtime.setPhase("FAILED");
    if (state.is_outdated) {
      runtime.setPhase("ANALYZING_REQUIREMENTS");
      state = await runtime.deps.clarification.analyze(state.requirement_revision);
    }
    if (shouldPause(state)) return pauseForClarification(runtime);
    if (state.continuation_state === "CONTINUE_EDITING") {
      await runtime.deps.clarification.chooseContinuation("CONTINUE_ANALYSIS");
    }
    runtime.deps.onCloseChat();
    await runSourceAndModel(runtime);
  } catch (error) {
    handleWorkflowError(error, runtime.setPhase, runtime.notifyError);
  }
}

export async function continueWorkflow(runtime: WorkflowRuntime): Promise<void> {
  runtime.deps.onCloseChat();
  try {
    await runtime.deps.clarification.chooseContinuation("CONTINUE_ANALYSIS");
    await runSourceAndModel(runtime);
  } catch (error) {
    runtime.deps.onOpenChat();
    handleWorkflowError(error, runtime.setPhase, runtime.notifyError);
  }
}

export async function resolveWorkflowCoverage(
  runtime: WorkflowRuntime,
  input: Parameters<WorkflowDependencies["analysis"]["resolveCoverage"]>[0],
): Promise<void> {
  try {
    await runtime.deps.analysis.resolveCoverage(input);
  } catch (error) {
    runtime.notifyError(isApiErrorCode(error));
  }
}

export async function recheckWorkflowCoverage(
  runtime: WorkflowRuntime,
  input: Parameters<WorkflowDependencies["analysis"]["recheckCoverage"]>[0],
): Promise<void> {
  try {
    runtime.setPhase("RECHECKING_SOURCE");
    const status = await runtime.deps.analysis.recheckCoverage(input);
    await continueWhenReady(runtime, status);
  } catch (error) {
    handleWorkflowError(error, runtime.setPhase, runtime.notifyError);
  }
}

async function runSourceAndModel(runtime: WorkflowRuntime): Promise<void> {
  runtime.setPhase("ANALYZING_SOURCE");
  await continueWhenReady(runtime, await runtime.deps.analysis.analyze());
}

function pauseForClarification(runtime: WorkflowRuntime): void {
  runtime.setPhase("WAITING_FOR_CLARIFICATION");
  runtime.deps.onOpenChat();
}

function isApiErrorCode(error: unknown): string | undefined {
  return isApiError(error) ? error.errorCode : undefined;
}
