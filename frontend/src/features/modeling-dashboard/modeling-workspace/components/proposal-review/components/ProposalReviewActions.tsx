"use client";

import React from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Check, Loader2, RefreshCw, X } from "lucide-react";

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
  const { t } = useTranslation("proposal-review");
  return (
    <div className="flex items-center justify-end gap-2 border-t border-slate-200 bg-slate-50/80 px-3.5 py-2.5 dark:border-slate-800 dark:bg-slate-900/60">
      <Button
        variant="outline"
        size="sm"
        onClick={onRetry}
        disabled={isSubmitting}
        className="rounded-lg border-slate-300 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 dark:hover:text-white"
      >
        <RefreshCw className="mr-1 size-3.5" />
        {t("BTN_RETRY_PROPOSAL", { defaultValue: "Yêu cầu AI làm lại" })}
      </Button>

      <Button
        variant="destructive"
        size="sm"
        onClick={onReject}
        disabled={isRejectDisabled || isSubmitting}
        className="rounded-lg text-xs font-semibold"
      >
        <X className="mr-1 size-3.5" />
        {t("BTN_REJECT_PROPOSAL", { defaultValue: "Từ chối" })}
      </Button>

      <Button
        variant="default"
        size="sm"
        onClick={onAccept}
        disabled={isAcceptDisabled || isSubmitting}
        className="rounded-lg bg-blue-600 px-4 text-xs font-bold text-white shadow-xs hover:bg-blue-500 dark:bg-sky-600 dark:hover:bg-sky-500"
      >
        {isSubmitting ? (
          <Loader2 className="mr-1 size-3.5 animate-spin" />
        ) : (
          <Check className="mr-1 size-3.5" />
        )}
        {t("BTN_ACCEPT_PROPOSAL", { defaultValue: "Chấp nhận thay đổi" })}
      </Button>
    </div>
  );
};
