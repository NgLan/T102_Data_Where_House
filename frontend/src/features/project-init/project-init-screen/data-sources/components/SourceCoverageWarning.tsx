import { AlertTriangle } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { SourceCoverageAssessmentResponse, SourceCoverageBatchResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import {
  groupCoverageAssessments,
  SourceCoverageRequirementGroup,
} from "./SourceCoverageRequirementGroup";

interface SourceCoverageWarningProps {
  batch: SourceCoverageBatchResponse;
  expectedSourceRevision: number;
  disabled: boolean;
  isStale: boolean;
  isRechecking: boolean;
  pendingItemIds: ReadonlySet<string>;
  itemErrors: ReadonlySet<string>;
  onResolve: (input: {
    assessmentId: string; batchId: string; expectedSourceRevision: number;
    expectedResolutionRevision: number;
    action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES"; candidateId?: string;
  }) => void;
  onRecheck: (input: { batchId: string; expectedSourceRevision: number }) => void;
  onUploadRequest: () => void;
  onEditRequirement: () => void;
}

/** Render one stable confirmation batch until explicit recheck replaces it. */
export function SourceCoverageWarning(props: SourceCoverageWarningProps) {
  const { t } = useTranslation("project-init");
  const groups = groupCoverageAssessments(props.batch.assessments);
  if (!groups.length) {
    return null;
  }
  const resolve = (item: SourceCoverageAssessmentResponse,
    action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES", candidateId?: string) =>
    props.onResolve({
      assessmentId: item.id, batchId: props.batch.id,
      expectedSourceRevision: props.expectedSourceRevision,
      expectedResolutionRevision: item.resolution_revision, action, candidateId,
    });
  return <section className="space-y-4 rounded-lg border border-amber-400 bg-amber-100/60 p-4 text-amber-950 dark:bg-amber-950/40 dark:text-amber-100">
    <header className="flex items-start gap-2">
      <AlertTriangle className="mt-0.5 size-5 shrink-0" aria-hidden />
      <div><h3 className="font-semibold">{t("TXT_SOURCE_COVERAGE_TITLE")}</h3>
        <p className="text-sm">{t(props.isStale
          ? "TXT_SOURCE_COVERAGE_STALE" : "TXT_SOURCE_COVERAGE_DESCRIPTION")}</p>
      </div>
    </header>
    {groups.map((items) => <SourceCoverageRequirementGroup key={items[0].requirement_id}
      title={items[0].requirement_title} assessments={items}
      disabled={props.disabled || props.isStale} pendingItemIds={props.pendingItemIds}
      itemErrors={props.itemErrors} onResolve={resolve}
      onUploadRequest={props.onUploadRequest} onEditRequirement={props.onEditRequirement} />)}
    {props.batch.confirmation_total > 0 && <footer className="space-y-3 border-t border-amber-300 pt-3">
      <p className="text-sm font-medium">{t("TXT_CONFIRMATION_PROGRESS", {
        resolved: props.batch.confirmation_resolved, total: props.batch.confirmation_total,
      })}</p>
      <div className="flex flex-wrap gap-2">
        <Button type="button" disabled={props.disabled || !props.batch.can_recheck}
          onClick={() => props.onRecheck({ batchId: props.batch.id,
            expectedSourceRevision: props.expectedSourceRevision })}>
          {t(props.isRechecking ? "TXT_WORKFLOW_RECHECKING_SOURCE" : "BTN_RECHECK_SOURCE_DATA")}
        </Button>
        <Button type="button" variant="outline" disabled={props.disabled}
          onClick={props.onUploadRequest}>{t("BTN_UPLOAD_SOURCE")}</Button>
        <Button type="button" variant="ghost" disabled={props.disabled}
          onClick={props.onEditRequirement}>{t("BTN_EDIT_REQUIREMENT")}</Button>
      </div>
    </footer>}
  </section>;
}
