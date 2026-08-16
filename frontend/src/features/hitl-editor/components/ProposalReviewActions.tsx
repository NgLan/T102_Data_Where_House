/**
 * Presentation Component: Nhóm nút hành động Accept / Reject Proposal trong HITL Modal
 */

import React from 'react';
import { Button } from '@/common/components/ui/button';
import { Check, X, RefreshCw, ShieldCheck, Loader2 } from 'lucide-react';

export interface ProposalReviewActionsProps {
  /** Vô hiệu hóa nút Accept khi chưa có đề xuất hoặc đề xuất đã lỗi thời (xung đột revision) */
  isAcceptDisabled: boolean;
  /** Vô hiệu hóa nút Reject khi chưa có đề xuất nào đang chờ duyệt */
  isRejectDisabled: boolean;
  /** Đang gửi yêu cầu Accept/Reject lên Backend */
  isSubmitting: boolean;
  onAccept: () => void;
  onReject: () => void;
  onRetry: () => void;
}

export const ProposalReviewActions: React.FC<ProposalReviewActionsProps> = ({
  isAcceptDisabled,
  isRejectDisabled,
  isSubmitting,
  onAccept,
  onReject,
  onRetry,
}) => {
  return (
    <div className="bg-slate-50/90 px-6 py-3.5 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
        <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
        <span>Xác nhận áp dụng đề xuất thay đổi vào Data Model chính thức (Human-in-the-Loop)</span>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={onRetry}
          disabled={isSubmitting}
          className="text-xs rounded-xl px-3 py-1.5 font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1 text-slate-600" /> {t('review.retry')}
        </Button>
        <Button
          variant="danger"
          size="sm"
          onClick={onReject}
          disabled={isRejectDisabled || isSubmitting}
          className="text-xs rounded-xl px-3 py-1.5 font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <X className="w-3.5 h-3.5 mr-1" /> {t('review.reject')}
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={onAccept}
          disabled={isAcceptDisabled || isSubmitting}
          className="text-xs rounded-xl px-4 py-1.5 font-bold shadow-xs disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
          ) : (
            <Check className="w-3.5 h-3.5 mr-1" />
          )}
          {t('review.accept')}
        </Button>
      </div>
    </div>
  );
};

