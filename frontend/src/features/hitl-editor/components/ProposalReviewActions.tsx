/**
 * Presentation Component: Nhóm nút hành động Accept / Reject Proposal trong HITL Modal
 */

import React from 'react';
import { Button } from '@/common/components/ui/button';
import { Check, X, RefreshCw, ShieldCheck } from 'lucide-react';

export interface ProposalReviewActionsProps {
  onAccept: () => void;
  onReject: () => void;
  onRetry: () => void;
}

export const ProposalReviewActions: React.FC<ProposalReviewActionsProps> = ({
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
        <Button variant="secondary" size="sm" onClick={onRetry} className="text-xs rounded-xl px-3 py-1.5 font-semibold">
          <RefreshCw className="w-3.5 h-3.5 mr-1 text-slate-600" /> Yêu cầu AI làm lại
        </Button>
        <Button variant="destructive" size="sm" onClick={onReject} className="text-xs rounded-xl px-3 py-1.5 font-semibold">
          <X className="w-3.5 h-3.5 mr-1" /> Hủy bỏ (Reject)
        </Button>
        <Button size="sm" onClick={onAccept} className="text-xs rounded-xl px-4 py-1.5 font-bold shadow-xs">
          <Check className="w-3.5 h-3.5 mr-1" /> Áp dụng thay đổi (Accept)
        </Button>
      </div>
    </div>
  );
};

