"use client";

import { useState } from "react";
import { CheckCircle2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { SourceCoverageAssessmentResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { candidateLabel, SourceCandidateForm } from "./SourceCandidateForm";

interface Props {
  assessment: SourceCoverageAssessmentResponse;
  disabled: boolean;
  pending: boolean;
  hasError: boolean;
  onResolve: (action: "CONFIRM_CANDIDATE" | "REJECT_ALL_CANDIDATES", candidateId?: string) => void;
}

/** Independent Source Confirmation item with persisted compact resolved state. */
export function SourceConfirmationCard(props: Props) {
  const { t } = useTranslation("project-init");
  const [editing, setEditing] = useState(props.assessment.confirmation_status === "PENDING");
  const [selected, setSelected] = useState(props.assessment.selected_candidate_id ?? undefined);
  const resolved = props.assessment.confirmation_status !== "PENDING";
  if (resolved && !editing) {
    return <ResolvedCard assessment={props.assessment} disabled={props.disabled}
      onChange={() => setEditing(true)} />;
  }
  const oneCandidate = props.assessment.candidates.length === 1;
  return (
    <article aria-busy={props.pending}
      className="rounded-md border border-amber-300 bg-background/80 p-4 text-sm">
      <h4 className="font-medium">{props.assessment.title}</h4>
      <p className="mt-1 text-muted-foreground">{props.assessment.explanation}</p>
      <p className="mt-3 font-medium">{props.assessment.question}</p>
      <SourceCandidateForm groupName={`coverage-${props.assessment.id}`}
        candidates={props.assessment.candidates} selected={selected}
        disabled={props.disabled || props.pending} onSelect={setSelected}
        confirmLabel={t(oneCandidate ? "BTN_USE_THIS_FIELD" : "BTN_CONFIRM_SELECTION")}
        rejectLabel={t(oneCandidate ? "BTN_FIELD_NOT_SUITABLE" : "BTN_NO_FIELD_SUITABLE")}
        onConfirm={(id) => props.onResolve("CONFIRM_CANDIDATE", id)}
        onReject={() => props.onResolve("REJECT_ALL_CANDIDATES")} />
      {props.pending && <p className="mt-2 text-xs">{t("TXT_SAVING_CONFIRMATION")}</p>}
      {props.hasError && <p role="alert" className="mt-2 text-xs text-destructive">
        {t("TXT_CONFIRMATION_SAVE_ERROR")}
      </p>}
    </article>
  );
}

function ResolvedCard(props: Pick<Props, "assessment" | "disabled"> & { onChange: () => void }) {
  const { t } = useTranslation("project-init");
  const selected = props.assessment.candidates.find(
    (item) => item.id === props.assessment.selected_candidate_id,
  );
  const detail = selected
    ? t("TXT_CONFIRMED_FIELD", { field: candidateLabel(selected) })
    : t("TXT_REJECTED_FIELDS");
  return <article className="rounded-md border border-emerald-300 bg-emerald-50/70 p-4 text-sm dark:bg-emerald-950/20">
    <p className="flex items-center gap-2 font-medium"><CheckCircle2 className="size-4" />
      {t("TXT_CONFIRMATION_RESOLVED")}</p>
    <h4 className="mt-2 font-medium">{props.assessment.title}</h4>
    <p className="mt-1 text-muted-foreground">{detail}</p>
    <Button className="mt-3" size="sm" type="button" variant="outline"
      disabled={props.disabled} onClick={props.onChange}>{t("BTN_CHANGE_CONFIRMATION")}</Button>
  </article>;
}
