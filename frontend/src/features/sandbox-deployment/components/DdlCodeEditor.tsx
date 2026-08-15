'use client';

import { useTranslation } from 'react-i18next';
import { Textarea } from '@/common/components/ui/textarea';
import { DdlActionsBar, type DdlActionsBarProps } from './DdlActionsBar';

export interface DdlCodeEditorProps extends DdlActionsBarProps {
  ddlCode: string;
  onChange: (value: string) => void;
}

/** Hiển thị editor SQL và thống kê source hiện hành.
 * @param props DDL source cùng callback chỉnh sửa và action toolbar.
 * @returns Editor tối có line number và footer được dịch.
 */
export function DdlCodeEditor({ ddlCode, onChange, ...actions }: DdlCodeEditorProps) {
  const { t } = useTranslation('sandbox-deployment');
  const lineCount = (ddlCode.match(/\n/g) ?? []).length + 1;
  return (
    <section className="flex min-h-[480px] flex-[7] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 shadow-xl shadow-slate-950/20">
      <DdlActionsBar {...actions} />
      <div className="relative flex min-h-0 flex-1 overflow-hidden font-mono text-slate-100">
        <div aria-hidden="true" className="w-12 select-none overflow-hidden border-r border-slate-800 bg-slate-950/80 py-4 pr-2 text-right text-[12.5px] leading-relaxed text-slate-600">{Array.from({ length: Math.max(lineCount, 20) }).map((_, index) => <div key={index}>{index + 1}</div>)}</div>
        <Textarea value={ddlCode} onChange={(event) => onChange(event.target.value)} spellCheck={false} aria-label={t('TXT_EDITOR_TITLE')} className="min-h-0 flex-1 resize-none rounded-none border-0 bg-transparent p-4 font-mono text-[13px] leading-relaxed text-sky-300 focus-visible:ring-0" />
      </div>
      <footer className="flex items-center justify-between border-t border-slate-800 bg-slate-950/90 px-4 py-1.5 font-mono text-[10px] text-slate-500"><span>{t('TXT_EDITOR_STATS', { lines: lineCount })}</span><span>{t('TXT_TARGET_DIALECT')}</span></footer>
    </section>
  );
}
