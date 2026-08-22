"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { handleApiError, type ChangeProposalDetailResponse, type DataModelResponse } from "@/api";
import { countDiff, diffLines, hasChanges } from "../utils/dbml-text-diff";
import {
  acceptProposal,
  rejectProposal,
  fetchPendingProposal,
} from "../services/proposal-api";

interface ProposalReviewOptions {
  projectId: string;
  /** Nạp mô hình vừa được duyệt vào editor và canvas. */
  onApplied: (snapshot: DataModelResponse) => void;
}

/** Quản lý vòng duyệt đề xuất của AI Agent theo `data_flow.md` Bước 5.
 *
 * @param options Callback nhận snapshot sau khi người dùng chấp nhận đề xuất.
 * @returns Đề xuất đang xem, kết quả so sánh khác biệt và các lệnh duyệt.
 * @remarks Đề xuất chỉ được áp vào `data_models` khi người dùng bấm Chấp nhận.
 */
export function useProposalReview(options: ProposalReviewOptions) {
  const { onApplied } = options;
  const [proposal, setProposal] = useState<ChangeProposalDetailResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitErrorCode, setSubmitErrorCode] = useState<string | null>(null);

  const toErrorCode = (error: unknown) =>
    handleApiError(error, { shouldNotify: false }).errorCode;

  useEffect(() => {
    void fetchPendingProposal(options.projectId)
      .then(setProposal)
      .catch((error: unknown) => setSubmitErrorCode(toErrorCode(error)));
  }, [options.projectId]);

  /** Hiển thị ngay đề xuất Agent vừa tạo, không cần gọi lại API. */
  const showProposal = useCallback((value: ChangeProposalDetailResponse) => {
    setProposal(value);
    setSubmitErrorCode(null);
  }, []);

  const accept = useCallback(async (): Promise<boolean> => {
    if (!proposal) return false;
    setIsSubmitting(true);
    setSubmitErrorCode(null);
    try {
      onApplied(await acceptProposal(proposal.id));
      setProposal(null);
      return true;
    } catch (error: unknown) {
      setSubmitErrorCode(toErrorCode(error));
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [onApplied, proposal]);

  const reject = useCallback(async (): Promise<boolean> => {
    if (!proposal) return false;
    setIsSubmitting(true);
    setSubmitErrorCode(null);
    try {
      await rejectProposal(proposal.id);
      setProposal(null);
      return true;
    } catch (error: unknown) {
      setSubmitErrorCode(toErrorCode(error));
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [proposal]);

  const diff = useMemo(
    () => (proposal ? diffLines(proposal.current_dbml, proposal.proposed_dbml) : []),
    [proposal],
  );
  const stats = useMemo(() => countDiff(diff), [diff]);

  return {
    proposal,
    diff,
    addedCount: stats.added,
    removedCount: stats.removed,
    hasDiff: hasChanges(diff),
    isOutdated: proposal?.is_outdated ?? false,
    isSubmitting,
    submitErrorCode,
    accept,
    reject,
    showProposal,
    dismiss: useCallback(() => setProposal(null), []),
  };
}
