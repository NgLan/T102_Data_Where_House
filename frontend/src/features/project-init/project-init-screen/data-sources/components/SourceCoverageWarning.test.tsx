// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { SourceCoverageAssessmentResponse, SourceCoverageBatchResponse } from "@/api";
import { SourceCoverageWarning } from "./SourceCoverageWarning";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));

afterEach(cleanup);

describe("SourceCoverageWarning", () => {
  it("keeps item loading and controls independent", () => {
    renderWarning(batch([multi, single]), { pendingItemIds: new Set([multi.id]) });
    const cards = screen.getAllByRole("article");
    expect(within(cards[0]).getByRole("button", { name: "BTN_CONFIRM_SELECTION" }))
      .toBeDisabled();
    expect(within(cards[1]).getByRole("button", { name: "BTN_USE_THIS_FIELD" }))
      .toBeEnabled();
  });

  it("sends an item-scoped resolution with optimistic revisions", () => {
    const onResolve = vi.fn();
    renderWarning(batch([multi]), { onResolve });
    fireEvent.click(screen.getAllByRole("radio")[0]);
    fireEvent.click(screen.getByRole("button", { name: "BTN_CONFIRM_SELECTION" }));
    expect(onResolve).toHaveBeenCalledWith({
      assessmentId: multi.id, batchId: "batch-1", expectedSourceRevision: 7,
      expectedResolutionRevision: 0, action: "CONFIRM_CANDIDATE",
      candidateId: "candidate-1",
    });
  });

  it("shows resolved progress and rechecks only when the batch is ready", () => {
    const onRecheck = vi.fn();
    renderWarning(batch([{ ...single, confirmation_status: "CONFIRMED",
      selected_candidate_id: "candidate-1", resolution_revision: 1 }], true), { onRecheck });
    expect(screen.getByText("TXT_CONFIRMATION_RESOLVED")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "BTN_RECHECK_SOURCE_DATA" }));
    expect(onRecheck).toHaveBeenCalledWith({ batchId: "batch-1", expectedSourceRevision: 7 });
  });

  it("uses direct actions for one candidate and no confirmation form for missing data", () => {
    renderWarning(batch([single, missing]));
    expect(screen.getByRole("button", { name: "BTN_USE_THIS_FIELD" })).toBeInTheDocument();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(screen.getAllByRole("button", { name: "BTN_UPLOAD_SOURCE" }).length).toBeGreaterThan(0);
  });
});

function renderWarning(value: SourceCoverageBatchResponse, overrides: Partial<Parameters<typeof SourceCoverageWarning>[0]> = {}) {
  const props: Parameters<typeof SourceCoverageWarning>[0] = {
    batch: value, expectedSourceRevision: 7, disabled: false, isStale: false,
    isRechecking: false, pendingItemIds: new Set(), itemErrors: new Set(),
    onResolve: vi.fn(), onRecheck: vi.fn(), onUploadRequest: vi.fn(),
    onEditRequirement: vi.fn(), ...overrides,
  };
  return render(<SourceCoverageWarning {...props} />);
}

function batch(assessments: SourceCoverageAssessmentResponse[], canRecheck = false): SourceCoverageBatchResponse {
  const resolved = assessments.filter((item) => item.confirmation_status !== "PENDING").length;
  return { id: "batch-1", evaluated_source_revision: 7,
    confirmation_total: assessments.filter((item) => item.coverage_status === "NEEDS_SOURCE_CONFIRMATION").length,
    confirmation_resolved: resolved, can_recheck: canRecheck, assessments };
}

const base: SourceCoverageAssessmentResponse = {
  id: "assessment-1", analytical_requirement_id: "analytical-1",
  requirement_id: "requirement-1", requirement_title: "Distinct patients",
  coverage_status: "NEEDS_SOURCE_CONFIRMATION", required_concept_key: "PATIENT_IDENTITY",
  title: "Identify a patient", explanation: "Count each patient once.",
  question: "Which field identifies a patient?", confirmation_status: "PENDING",
  selected_candidate_id: null, resolution_revision: 0, candidates: [],
};
const candidate = { id: "candidate-1", kind: "COLUMN" as const, source_id: "source-1",
  source_name: "visits.csv", table_name: "visits", column_name: "record_no",
  from_column: null, to_column: null };
const multi = { ...base, candidates: [candidate, { ...candidate, id: "candidate-2", column_name: "patient_no" }] };
const single = { ...base, id: "assessment-2", candidates: [candidate] };
const missing = { ...base, id: "assessment-3", coverage_status: "MISSING_SOURCE" as const,
  confirmation_status: null, question: null, candidates: [], title: "Patient identity is missing" };
