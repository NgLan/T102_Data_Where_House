// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type {
  SourceConfirmationQuestionType,
  SourceCoverageAssessmentResponse,
  SourceCoverageBatchResponse,
  SourceCoverageReferenceResponse,
} from "@/api";
import { SourceCoverageWarning } from "./SourceCoverageWarning";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));

afterEach(cleanup);

describe("SourceCoverageWarning", () => {
  it("renders controls from question type instead of candidate count", () => {
    renderWarning(batch([singleField, fieldSet, businessChoice, singleCandidate, relationship]));
    expect(screen.getAllByRole("radio")).toHaveLength(4);
    expect(screen.getByRole("button", { name: "BTN_USE_FIELDS" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "BTN_USE_THIS_FIELD" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "BTN_USE_RELATIONSHIP" })).toBeEnabled();
    expect(screen.getByText("Treatment start")).toBeInTheDocument();
    expect(screen.getByText("Receiving department")).toBeInTheDocument();
  });

  it("sends the selected complete mapping with optimistic revisions", () => {
    const onResolve = vi.fn();
    renderWarning(batch([businessChoice]), { onResolve });
    fireEvent.click(screen.getAllByRole("radio")[0]);
    fireEvent.click(screen.getByRole("button", { name: "BTN_CONFIRM_SELECTION" }));
    expect(onResolve).toHaveBeenCalledWith({
      assessmentId: businessChoice.id, batchId: "batch-1", expectedSourceRevision: 7,
      expectedResolutionRevision: 0, action: "CONFIRM_CANDIDATE",
      candidateId: "candidate-1",
    });
  });

  it("keeps direct items independent and displays complete resolved evidence", () => {
    const resolved = { ...fieldSet, confirmation_status: "CONFIRMED" as const,
      selected_candidate_id: "candidate-set", resolution_revision: 1 };
    renderWarning(batch([resolved, singleCandidate], true), {
      pendingItemIds: new Set([singleCandidate.id]),
    });
    expect(screen.getByText("TXT_CONFIRMATION_RESOLVED")).toBeInTheDocument();
    expect(screen.getByText("Treatment end")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "BTN_USE_THIS_FIELD" })).toBeDisabled();
  });

  it("does not render confirmation controls for missing source", () => {
    renderWarning(batch([missing]));
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(screen.getAllByRole("button", { name: "BTN_UPLOAD_SOURCE" }).length).toBeGreaterThan(0);
  });
});

function renderWarning(value: SourceCoverageBatchResponse,
  overrides: Partial<Parameters<typeof SourceCoverageWarning>[0]> = {}) {
  return render(<SourceCoverageWarning batch={value} expectedSourceRevision={7}
    disabled={false} isStale={false} isRechecking={false}
    pendingItemIds={new Set()} itemErrors={new Set()} onResolve={vi.fn()}
    onRecheck={vi.fn()} onUploadRequest={vi.fn()} onEditRequirement={vi.fn()}
    {...overrides} />);
}

function batch(assessments: SourceCoverageAssessmentResponse[], canRecheck = false) {
  const confirmations = assessments.filter((item) => item.coverage_status === "NEEDS_SOURCE_CONFIRMATION");
  return { id: "batch-1", evaluated_source_revision: 7,
    confirmation_total: confirmations.length,
    confirmation_resolved: confirmations.filter((item) => item.confirmation_status !== "PENDING").length,
    can_recheck: canRecheck, assessments };
}

function assessment(id: string, type: SourceConfirmationQuestionType,
  candidates: SourceCoverageAssessmentResponse["candidates"]): SourceCoverageAssessmentResponse {
  return { id, analytical_requirement_id: "analytical-1", requirement_id: "requirement-1",
    requirement_title: "Treatment analysis", coverage_status: "NEEDS_SOURCE_CONFIRMATION",
    required_concept_key: id.toUpperCase(), title: "Confirm mapping", explanation: "Meaning matters.",
    question: "Which answer applies?", question_type: type, confirmation_status: "PENDING",
    selected_candidate_id: null, resolution_revision: 0, candidates };
}

const column: SourceCoverageReferenceResponse = { kind: "COLUMN", source_id: "source-1",
  source_name: "visits.csv", table_name: "visits", column_name: "record_no" };
const option = (id: string, label: string, references = [column]) => ({ id, label, references });
const singleField = assessment("single-field", "SINGLE_FIELD_SELECTION",
  [option("candidate-1", "Patient record"), option("candidate-2", "Medical record")]);
const businessChoice = assessment("business-choice", "BUSINESS_SEMANTIC_CHOICE",
  [option("candidate-1", "Receiving department"), option("candidate-2", "Discharge department")]);
const fieldSet = assessment("field-set", "FIELD_SET_CONFIRMATION", [option(
  "candidate-set", "Treatment duration", [
    { ...column, column_name: "admitted_at", role_key: "START_TIME", role_label: "Treatment start" },
    { ...column, column_name: "discharged_at", role_key: "END_TIME", role_label: "Treatment end" },
  ])]);
const singleCandidate = assessment("single-candidate", "SINGLE_CANDIDATE_CONFIRMATION",
  [option("candidate-status", "Stored record status")]);
const relationship = assessment("relationship", "RELATIONSHIP_CONFIRMATION", [option(
  "candidate-relation", "Patient to archive", [{ kind: "RELATIONSHIP", source_id: "source-1",
    source_name: "visits.csv", from_column: "visits.record_no", to_column: "archive.record_no" }],
)]);
const missing = { ...singleCandidate, id: "missing", coverage_status: "MISSING_SOURCE" as const,
  confirmation_status: null, question: null, question_type: null, candidates: [] };
