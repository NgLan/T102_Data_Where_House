import type { SourceCoverageCandidateResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { SourceCandidateDetails } from "./SourceCandidateDetails";

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

/** Radio controls chỉ dành cho các question type có lựa chọn loại trừ nhau. */
export function SourceSelectionForm(props: Props) {
  return <div className="mt-3 space-y-3">
    <fieldset className="space-y-2" disabled={props.disabled}>
      {props.candidates.map((candidate) => (
        <label key={candidate.id}
          className="flex cursor-pointer items-center gap-3 rounded-md border p-3 hover:bg-muted/60 transition-colors">
          <input type="radio" name={props.groupName}
            checked={props.selected === candidate.id}
            onChange={() => props.onSelect(candidate.id)} className="cursor-pointer shrink-0" />
          <div className="flex-1 min-w-0">
            <SourceCandidateDetails candidate={candidate} />
          </div>
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
