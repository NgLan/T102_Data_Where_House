"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppNotification } from "@/common/notifications";
import { createWorkflowHref } from "@/common/routing/workflow-routing";
import {
  continueWorkflow,
  recheckWorkflowCoverage,
  resolveWorkflowCoverage,
  runWorkflow,
  type WorkflowDependencies,
  type WorkflowRuntime,
} from "./project-init-workflow-actions";
import type { ProjectInitPhase } from "./project-init-workflow-helpers";

export type { ProjectInitPhase } from "./project-init-workflow-helpers";

/** Điều phối Project Init bằng persisted readiness; không dùng browser storage/error details. */
export function useProjectInitWorkflow(deps: WorkflowDependencies) {
  const router = useRouter();
  const { notifyError, notifyWarning } = useAppNotification();
  const [phase, setPhase] = useState<ProjectInitPhase>("IDLE");
  const status = deps.analysis.statusQuery.data;
  const runtime: WorkflowRuntime = {
    deps,
    setPhase,
    notifyError,
    notifyWarning,
    onReady: () => router.push(createWorkflowHref("modeling", deps.projectId)),
  };
  const batch = status?.source_coverage_batch;
  const blockers = batch?.assessments
    .filter((item) => item.coverage_status !== "SUPPORTED") ?? [];
  const terminal = ["IDLE", "FAILED", "SOURCE_CONFIRMATION_REQUIRED",
    "SOURCE_DATA_REQUIRED", "WAITING_FOR_CLARIFICATION"];
  return {
    phase,
    sourceCoverageBatch: batch && blockers.length > 0 ? { ...batch, assessments: blockers } : null,
    isSourceCoverageStale: status?.source_analysis_outdated ?? false,
    sourceRevision: status?.source_revision ?? 0,
    isRunning: !terminal.includes(phase),
    run: () => runWorkflow(runtime),
    continueAnalysis: () => continueWorkflow(runtime),
    resolveCoverage: (
      input: Parameters<WorkflowDependencies["analysis"]["resolveCoverage"]>[0],
    ) => resolveWorkflowCoverage(runtime, input),
    recheckCoverage: (
      input: Parameters<WorkflowDependencies["analysis"]["recheckCoverage"]>[0],
    ) => recheckWorkflowCoverage(runtime, input),
  };
}
