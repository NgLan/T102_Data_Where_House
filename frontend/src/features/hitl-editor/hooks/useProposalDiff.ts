/**
 * Custom Hook nạp đề xuất thay đổi đang chờ duyệt, tính khác biệt DBML (T-031)
 * và thực hiện chấp nhận / từ chối đề xuất (T-032 / T-033)
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { countDiff, diffLines, hasChanges } from '@/common/utils/text-diff';
import {
  acceptProposalApi,
  getChangeProposalApi,
  listChangeProposalsApi,
  rejectProposalApi,
} from '../services/hitl-api';
import { ChangeProposalDetailDto } from '../types/hitl.types';

/** Trích mã lỗi chuẩn hóa từ error envelope của Backend */
function toErrorCode(error: unknown): string {
  return (error as { error_code?: string })?.error_code ?? 'UNKNOWN_ERROR';
}

export function useProposalDiff() {
  const dataModel = useProjectStore((state) => state.dataModel);
  const setDataModel = useProjectStore((state) => state.setDataModel);

  const [proposal, setProposal] = useState<ChangeProposalDetailDto | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitErrorCode, setSubmitErrorCode] = useState<string | null>(null);

  /**
   * Lấy đề xuất PROPOSED mới nhất của mô hình dữ liệu rồi nạp chi tiết để so sánh.
   * Backend đã sắp xếp danh sách mới nhất trước nên chỉ cần lấy phần tử đầu tiên.
   */
  const loadLatestProposal = useCallback(async () => {
    if (!dataModel) {
      setProposal(null);
      return;
    }

    setIsLoading(true);
    setErrorCode(null);
    try {
      const summaries = await listChangeProposalsApi(dataModel.id, 'PROPOSED');
      if (summaries.length === 0) {
        setProposal(null);
        return;
      }
      setProposal(await getChangeProposalApi(summaries[0].id));
    } catch (error) {
      setErrorCode(toErrorCode(error));
      setProposal(null);
    } finally {
      setIsLoading(false);
    }
  }, [dataModel]);

  useEffect(() => {
    void loadLatestProposal();
  }, [loadLatestProposal]);

  /**
   * Chấp nhận đề xuất: áp dụng DBML mới vào mô hình dữ liệu chính thức (T-032).
   * Cập nhật store bằng mô hình mới do Backend trả về để mọi màn hình khác (ERD, DDL)
   * tự đồng bộ theo revision mới.
   */
  const acceptProposal = useCallback(async (): Promise<boolean> => {
    if (!proposal) return false;

    setIsSubmitting(true);
    setSubmitErrorCode(null);
    try {
      const updated = await acceptProposalApi(proposal.id);
      setDataModel({ id: updated.id, dbml: updated.dbml, revision: updated.revision });
      await loadLatestProposal();
      return true;
    } catch (error) {
      setSubmitErrorCode(toErrorCode(error));
      await loadLatestProposal();
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [proposal, setDataModel, loadLatestProposal]);

  /**
   * Từ chối đề xuất (T-033): chỉ đổi trạng thái đề xuất, mô hình dữ liệu giữ nguyên.
   */
  const rejectProposal = useCallback(async (): Promise<boolean> => {
    if (!proposal) return false;

    setIsSubmitting(true);
    setSubmitErrorCode(null);
    try {
      await rejectProposalApi(proposal.id);
      await loadLatestProposal();
      return true;
    } catch (error) {
      setSubmitErrorCode(toErrorCode(error));
      await loadLatestProposal();
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [proposal, loadLatestProposal]);

  // Tính khác biệt giữa DBML hiện hành và DBML được đề xuất
  const diff = useMemo(() => {
    if (!proposal) return [];
    return diffLines(proposal.current_dbml, proposal.proposed_dbml);
  }, [proposal]);

  const stats = useMemo(() => countDiff(diff), [diff]);

  return {
    proposal,
    diff,
    addedCount: stats.added,
    removedCount: stats.removed,
    hasDiff: hasChanges(diff),
    isOutdated: proposal?.is_outdated ?? false,
    isLoading,
    errorCode,
    isSubmitting,
    submitErrorCode,
    acceptProposal,
    rejectProposal,
    reloadProposal: loadLatestProposal,
  };
}
