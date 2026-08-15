'use client';

import { Code2, Copy, Download, FileText, Wand2 } from 'lucide-react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';

export interface DdlActionsBarProps {
  onFormat: () => void;
  onCopy: () => void;
  onDownloadDoc: () => void;
  onDownloadSql: () => void;
}

/** Hiển thị các action của DDL editor.
 * @param props Callback định dạng, sao chép và tải file.
 * @returns Toolbar sử dụng shadcn Button.
 */
export function DdlActionsBar(props: DdlActionsBarProps) {
  const { t } = useTranslation('sandbox-deployment');
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-200">
      <div className="flex items-center gap-2 text-xs font-bold tracking-wide"><Code2 className="size-4 text-sky-400" /><span>{t('TXT_EDITOR_TITLE')}</span><span className="rounded border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] text-emerald-400">{t('TXT_EDITABLE')}</span></div>
      <div className="flex flex-wrap items-center gap-2">
        <ActionButton icon={<Wand2 />} label={t('BTN_FORMAT_SQL')} onClick={props.onFormat} />
        <ActionButton icon={<Copy />} label={t('BTN_COPY_DDL')} onClick={props.onCopy} />
        <ActionButton icon={<FileText />} label={t('BTN_DOWNLOAD_DOC')} onClick={props.onDownloadDoc} />
        <ActionButton icon={<Download />} label={t('BTN_DOWNLOAD_SQL')} onClick={props.onDownloadSql} />
      </div>
    </div>
  );
}

function ActionButton({ icon, label, onClick }: { icon: ReactNode; label: string; onClick: () => void }) {
  return <Button type="button" size="sm" variant="secondary" onClick={onClick}>{icon}{label}</Button>;
}
