/**
 * Presentation Component: Khung so sánh khác biệt DBML được AI đề xuất (UC6.1 / FR5.3)
 * Dòng thêm mới tô nền xanh, dòng bị xóa tô nền đỏ — giống trải nghiệm xem diff của code.
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, GitCompare, Loader2, Columns2, AlignJustify } from 'lucide-react';
import { DiffLine } from '@/common/utils/text-diff';
import { ChangeProposalDetailDto, DiffViewMode } from '../types/hitl.types';

export interface DbmlDiffViewerProps {
  proposal: ChangeProposalDetailDto | null;
  diff: DiffLine[];
  addedCount: number;
  removedCount: number;
  hasDiff: boolean;
  isLoading: boolean;
  errorCode: string | null;
  /** Lỗi phát sinh khi bấm Accept/Reject — hiển thị thành dải cảnh báo, không nuốt khung diff */
  submitErrorCode?: string | null;
}

/** Bảng màu nền/chữ theo loại thay đổi của từng dòng */
const LINE_STYLES: Record<DiffLine['type'], string> = {
  added: 'bg-emerald-500/10 text-emerald-300',
  removed: 'bg-rose-500/10 text-rose-300',
  unchanged: 'text-slate-400',
};

/** Ký hiệu tiền tố hiển thị đầu mỗi dòng */
const LINE_MARKERS: Record<DiffLine['type'], string> = {
  added: '+',
  removed: '-',
  unchanged: ' ',
};

export const DbmlDiffViewer: React.FC<DbmlDiffViewerProps> = ({
  proposal,
  diff,
  addedCount,
  removedCount,
  hasDiff,
  isLoading,
  errorCode,
  submitErrorCode = null,
}) => {
  const { t } = useTranslation('hitlEditor');
  const { t: tErrors } = useTranslation('errors');
  const [mode, setMode] = useState<DiffViewMode>('unified');

  const submitBanner = submitErrorCode ? (
    <div className="flex items-start gap-2 px-3.5 py-2.5 bg-rose-500/10 border-b border-rose-500/30 text-[11px] text-rose-300">
      <AlertTriangle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
      <span>{tErrors(submitErrorCode, { defaultValue: tErrors('UNKNOWN_ERROR') })}</span>
    </div>
  ) : null;

  if (isLoading) {
    return <DiffPlaceholder icon={<Loader2 className="w-4 h-4 animate-spin" />} message={t('diff.loading')} />;
  }

  if (errorCode) {
    return (
      <DiffPlaceholder
        icon={<AlertTriangle className="w-4 h-4 text-rose-400" />}
        message={tErrors(errorCode, { defaultValue: t('diff.load_failed') })}
      />
    );
  }

  if (!proposal) {
    return (
      <div className="flex flex-col h-full overflow-hidden rounded-xl border border-slate-800 bg-[#090d16]">
        {submitBanner}
        <DiffPlaceholder icon={<GitCompare className="w-4 h-4" />} message={t('diff.empty')} />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden rounded-xl border border-slate-800 bg-[#090d16]">
      {submitBanner}

      {/* Thanh tiêu đề: revision, thống kê +/- và nút đổi chế độ hiển thị */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-900/90 px-3.5 py-2.5 border-b border-slate-800/80">
        <div className="flex flex-wrap items-center gap-2 text-xs font-bold text-slate-100">
          <GitCompare className="w-4 h-4 text-indigo-400" />
          <span>{t('diff.title')}</span>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {t('diff.base_revision', { revision: proposal.base_revision })}
          </span>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {t('diff.current_revision', { revision: proposal.current_revision })}
          </span>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
            {t(`status.${proposal.status}`)}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono font-bold">
            <span className="text-emerald-400">+{addedCount}</span>
            <span className="text-slate-600"> / </span>
            <span className="text-rose-400">−{removedCount}</span>
          </span>
          <button
            onClick={() => setMode(mode === 'unified' ? 'split' : 'unified')}
            className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
          >
            {mode === 'unified' ? (
              <>
                <Columns2 className="w-3.5 h-3.5 text-sky-400" /> {t('diff.mode_split')}
              </>
            ) : (
              <>
                <AlignJustify className="w-3.5 h-3.5 text-sky-400" /> {t('diff.mode_unified')}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Dải cảnh báo khi đề xuất dựa trên revision đã cũ (Edge case 1 & 5) */}
      {proposal.is_outdated && (
        <div className="flex items-start gap-2 px-3.5 py-2.5 bg-rose-500/10 border-b border-rose-500/30 text-[11px] text-rose-300">
          <AlertTriangle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
          <div>
            <div className="font-bold">{t('outdated_warning.title')}</div>
            <p className="m-0 mt-0.5 text-rose-200/90">
              {t('outdated_warning.message', {
                baseRevision: proposal.base_revision,
                currentRevision: proposal.current_revision,
              })}
            </p>
          </div>
        </div>
      )}

      {!hasDiff && (
        <div className="px-3.5 py-2 bg-slate-800/40 border-b border-slate-800 text-[11px] text-slate-400">
          {t('diff.no_change')}
        </div>
      )}

      {mode === 'unified' ? (
        <UnifiedDiff diff={diff} />
      ) : (
        <SplitDiff diff={diff} currentLabel={t('diff.column_current')} proposedLabel={t('diff.column_proposed')} />
      )}
    </div>
  );
};

/**
 * Khung trạng thái rỗng / đang tải / lỗi của khung so sánh.
 */
const DiffPlaceholder: React.FC<{ icon: React.ReactNode; message: string }> = ({ icon, message }) => (
  <div className="flex flex-col items-center justify-center gap-2 h-full rounded-xl border border-slate-800 bg-[#090d16] text-slate-400 text-xs p-6 text-center">
    {icon}
    <span>{message}</span>
  </div>
);

/**
 * Chế độ hiển thị gộp (Unified): mọi thay đổi nằm trên cùng một cột.
 */
const UnifiedDiff: React.FC<{ diff: DiffLine[] }> = ({ diff }) => (
  <div className="flex-1 overflow-auto dark-scrollbar font-mono text-[12.5px] leading-relaxed py-2">
    {diff.map((line, index) => (
      <div key={index} className={`flex ${LINE_STYLES[line.type]}`}>
        <span className="w-10 shrink-0 pr-2 text-right text-slate-600 select-none">
          {line.oldLineNo ?? ''}
        </span>
        <span className="w-10 shrink-0 pr-2 text-right text-slate-600 select-none">
          {line.newLineNo ?? ''}
        </span>
        <span className="w-4 shrink-0 select-none font-bold">{LINE_MARKERS[line.type]}</span>
        <span className="flex-1 whitespace-pre pr-4">{line.text || ' '}</span>
      </div>
    ))}
  </div>
);

/**
 * Chế độ hiển thị tách đôi (Split): DBML hiện hành bên trái, DBML đề xuất bên phải.
 */
const SplitDiff: React.FC<{ diff: DiffLine[]; currentLabel: string; proposedLabel: string }> = ({
  diff,
  currentLabel,
  proposedLabel,
}) => (
  <div className="flex flex-col flex-1 overflow-hidden">
    <div className="flex text-[10px] font-bold uppercase tracking-wide text-slate-500 border-b border-slate-800 bg-slate-900/60">
      <div className="flex-1 px-3 py-1.5 border-r border-slate-800">{currentLabel}</div>
      <div className="flex-1 px-3 py-1.5">{proposedLabel}</div>
    </div>
    <div className="flex-1 overflow-auto dark-scrollbar font-mono text-[12.5px] leading-relaxed py-2">
      {diff.map((line, index) => (
        <div key={index} className="flex">
          <div
            className={`flex flex-1 border-r border-slate-800/60 ${
              line.type === 'added' ? 'bg-slate-900/30' : LINE_STYLES[line.type]
            }`}
          >
            <span className="w-10 shrink-0 pr-2 text-right text-slate-600 select-none">
              {line.oldLineNo ?? ''}
            </span>
            <span className="flex-1 whitespace-pre pr-2">
              {line.type === 'added' ? '' : line.text || ' '}
            </span>
          </div>
          <div
            className={`flex flex-1 ${
              line.type === 'removed' ? 'bg-slate-900/30' : LINE_STYLES[line.type]
            }`}
          >
            <span className="w-10 shrink-0 pr-2 text-right text-slate-600 select-none">
              {line.newLineNo ?? ''}
            </span>
            <span className="flex-1 whitespace-pre pr-2">
              {line.type === 'removed' ? '' : line.text || ' '}
            </span>
          </div>
        </div>
      ))}
    </div>
  </div>
);
