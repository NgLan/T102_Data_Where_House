/**
 * Custom Hook nạp đề xuất thay đổi đang chờ duyệt và tính khác biệt DBML (UC6.1 / T-031)
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { countDiff, diffLines, hasChanges } from '@/common/utils/text-diff';
import { getChangeProposalApi, listChangeProposalsApi } from '../services/hitl-api';
import { ChangeProposalDetailDto } from '../types/hitl.types';

export function useProposalDiff() {
  const dataModel = useProjectStore((state) => state.dataModel);

  const [proposal, setProposal] = useState<ChangeProposalDetailDto | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);

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
      const code = (error as { error_code?: string })?.error_code ?? 'UNKNOWN_ERROR';
      setErrorCode(code);
      setProposal(null);
    } finally {
      setIsLoading(false);
    }
  }, [dataModel]);

  useEffect(() => {
    void loadLatestProposal();
  }, [loadLatestProposal]);

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
    reloadProposal: loadLatestProposal,
  };
}
