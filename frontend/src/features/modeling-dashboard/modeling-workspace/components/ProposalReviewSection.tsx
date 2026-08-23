import { DbmlDiffViewer } from "./proposal-review/components/DbmlDiffViewer";
import { ProposalReviewActions } from "./proposal-review/components/ProposalReviewActions";
import type { useProposalReview } from "./proposal-review/hooks/use-proposal-review";

interface ProposalReviewSectionProps {
  review: ReturnType<typeof useProposalReview>;
}

/** Ghép diff và actions của một proposal đang chờ duyệt một cách liền mạch, không lồng viền thừa. */
export function ProposalReviewSection({ review }: ProposalReviewSectionProps) {
  if (!review.proposal) return null;
  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
        <DbmlDiffViewer
          proposal={review.proposal}
          diff={review.diff}
          addedCount={review.addedCount}
          removedCount={review.removedCount}
          hasDiff={review.hasDiff}
          submitErrorCode={review.submitErrorCode}
        />
      </div>
      <ProposalReviewActions
        isAcceptDisabled={review.isOutdated}
        isRejectDisabled={false}
        isSubmitting={review.isSubmitting}
        onAccept={() => void review.accept()}
        onReject={() => void review.reject()}
        onRetry={review.dismiss}
      />
    </section>
  );
}
