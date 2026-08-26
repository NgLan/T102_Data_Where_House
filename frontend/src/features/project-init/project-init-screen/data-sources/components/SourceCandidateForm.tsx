"use client";

import type { SourceCoverageCandidateResponse } from "@/api";
import { Button } from "@/common/components/ui/button";

interface Props {
  groupName: string;
  candidates: SourceCoverageCandidateResponse[];
  selected?: string;
  disabled: boolean;
  confirmLabel: string;
  rejectLabel: string;
  onSelect: (id: string) => void;
  onConfirm: (id: string) => void;
  onReject: () => void;
}

/** Candidate controls adapt to one or multiple exact source references. */
export function SourceCandidateForm(props: Props) {
  if (props.candidates.length === 1) {
    const candidate = props.candidates[0];
    return <div className="mt-3 space-y-3">
      <p className="rounded-md border p-3">{candidateLabel(candidate)}</p>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" type="button" disabled={props.disabled}
          onClick={() => props.onConfirm(candidate.id)}>{props.confirmLabel}</Button>
        <Button size="sm" type="button" variant="outline" disabled={props.disabled}
          onClick={props.onReject}>{props.rejectLabel}</Button>
      </div>
    </div>;
  }
  return <div className="mt-3 space-y-3">
    <fieldset className="space-y-2" disabled={props.disabled}>
      {props.candidates.map((candidate) => (
        <label key={candidate.id}
          className="flex cursor-pointer items-start gap-2 rounded-md border p-3 hover:bg-muted/60">
          <input type="radio" name={props.groupName}
            checked={props.selected === candidate.id}
            onChange={() => props.onSelect(candidate.id)} className="mt-0.5" />
          <span>{candidateLabel(candidate)}</span>
        </label>
      ))}
    </fieldset>
    <div className="flex flex-wrap gap-2">
      <Button size="sm" type="button" disabled={props.disabled || !props.selected}
        onClick={() => props.selected && props.onConfirm(props.selected)}>
        {props.confirmLabel}
      </Button>
      <Button size="sm" type="button" variant="outline" disabled={props.disabled}
        onClick={props.onReject}>{props.rejectLabel}</Button>
    </div>
  </div>;
}

export function candidateLabel(candidate: SourceCoverageCandidateResponse): string {
  if (candidate.kind === "COLUMN") {
    return `${candidate.source_name} · ${candidate.table_name}.${candidate.column_name}`;
  }
  return `${candidate.source_name} · ${candidate.from_column} → ${candidate.to_column}`;
}
