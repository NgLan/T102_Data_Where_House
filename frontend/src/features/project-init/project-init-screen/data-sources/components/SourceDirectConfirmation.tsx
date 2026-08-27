import type { SourceCoverageCandidateResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { SourceCandidateDetails } from "./SourceCandidateDetails";

interface Props {
  candidate: SourceCoverageCandidateResponse;
  disabled: boolean;
  confirmLabel: string;
  rejectLabel: string;
  onConfirm: (id: string) => void;
  onReject: () => void;
}

/** Confirm/reject trực tiếp một mapping hoàn chỉnh, không dùng radio. */
export function SourceDirectConfirmation(props: Props) {
  return <div className="mt-3 space-y-3">
    <div className="rounded-md border p-3">
      <SourceCandidateDetails candidate={props.candidate} />
    </div>
    <div className="flex flex-wrap gap-2">
      <Button size="sm" type="button" disabled={props.disabled}
        onClick={() => props.onConfirm(props.candidate.id)}>{props.confirmLabel}</Button>
      <Button size="sm" type="button" variant="outline" disabled={props.disabled}
        onClick={props.onReject}>{props.rejectLabel}</Button>
    </div>
  </div>;
}
