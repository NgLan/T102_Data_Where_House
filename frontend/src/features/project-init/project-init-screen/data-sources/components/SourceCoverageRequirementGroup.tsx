import type { SourceCoverageAssessmentResponse } from "@/api";
import { useTranslation } from "react-i18next";
import { MissingSourceCard } from "./MissingSourceCard";
import { SourceConfirmationCard } from "./SourceConfirmationCard";

interface Props {
  title: string;
  assessments: SourceCoverageAssessmentResponse[];
  disabled: boolean;
  pendingItemIds: ReadonlySet<string>;
  itemErrors: ReadonlySet<string>;
  onResolve: (assessment: SourceCoverageAssessmentResponse,
    action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES", candidateId?: string) => void;
  onUploadRequest: () => void;
  onEditRequirement: () => void;
}

/** Group blocker cards under one canonical Requirement title. */
export function SourceCoverageRequirementGroup(props: Props) {
  const { t } = useTranslation("project-init");
  return <section className="space-y-3">
    <header>
      <h4 className="font-semibold">{props.title}</h4>
      <p className="text-xs text-muted-foreground">{t("TXT_CONFIRMATION_ITEMS_COUNT", {
        count: props.assessments.length,
      })}</p>
    </header>
    {props.assessments.map((assessment) =>
      assessment.coverage_status === "NEEDS_SOURCE_CONFIRMATION" ? (
        <SourceConfirmationCard key={`${assessment.id}-${assessment.resolution_revision}`}
          assessment={assessment}
          disabled={props.disabled} pending={props.pendingItemIds.has(assessment.id)}
          hasError={props.itemErrors.has(assessment.id)}
          onResolve={(action, candidateId) => props.onResolve(assessment, action, candidateId)} />
      ) : (
        <MissingSourceCard key={assessment.id} assessment={assessment}
          disabled={props.disabled} onUploadRequest={props.onUploadRequest}
          onEditRequirement={props.onEditRequirement} />
      ))}
  </section>;
}

export function groupCoverageAssessments(items: SourceCoverageAssessmentResponse[]) {
  const groups = new Map<string, SourceCoverageAssessmentResponse[]>();
  for (const item of items) {
    const current = groups.get(item.requirement_id) ?? [];
    current.push(item);
    groups.set(item.requirement_id, current);
  }
  return [...groups.values()];
}
