/**
 * Presentation Component: Nhóm nút hành động Accept / Reject Proposal trong HITL Modal
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';
import { Check, X, RefreshCw, ShieldCheck } from 'lucide-react';

export interface ProposalReviewActionsProps {
  /** Vô hiệu hóa nút Accept khi chưa có đề xuất hoặc đề xuất đã lỗi thời (xung đột revision) */
  isAcceptDisabled: boolean;
  onAccept: () => void;
  onReject: () => void;
  onRetry: () => void;
}

export const ProposalReviewActions: React.FC<ProposalReviewActionsProps> = ({
  isAcceptDisabled,
  onAccept,
  onReject,
  onRetry,
}) => {
  const { t } = useTranslation('hitlEditor');

  return (
    <div className="bg-slate-50/90 px-6 py-3.5 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
        <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
        <span>{t('review.hint')}</span>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={onRetry} className="text-xs rounded-xl px-3 py-1.5 font-semibold">
          <RefreshCw className="w-3.5 h-3.5 mr-1 text-slate-600" /> {t('review.retry')}
        </Button>
        <Button variant="danger" size="sm" onClick={onReject} className="text-xs rounded-xl px-3 py-1.5 font-semibold">
          <X className="w-3.5 h-3.5 mr-1" /> {t('review.reject')}
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={onAccept}
          disabled={isAcceptDisabled}
          className="text-xs rounded-xl px-4 py-1.5 font-bold shadow-xs disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Check className="w-3.5 h-3.5 mr-1" /> {t('review.accept')}
        </Button>
      </div>
    </div>
  );
};
