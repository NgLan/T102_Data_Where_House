/**
 * Presentation Component: DDL Code Editor (Cột trái Step 3)
 * Full-height SQL Editor với DdlActionsBar, line numbers, cảnh báo tương thích dialect & trạng thái tải
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { DdlActionsBar, DdlActionsBarProps } from './DdlActionsBar';

export interface DdlCodeEditorProps extends DdlActionsBarProps {
  ddlCode: string;
  onChange: (value: string) => void;
  schemaName: string;
  tableCount: number;
  revision: number;
  warnings: string[];
  errorCode: string | null;
}

export const DdlCodeEditor: React.FC<DdlCodeEditorProps> = ({
  ddlCode,
  onChange,
  schemaName,
  tableCount,
  revision,
  warnings,
  errorCode,
  dialect,
  onDialectChange,
  isGenerating,
  isDownloadDisabled,
  onFormat,
  onCopy,
  onDownloadDoc,
  onDownloadSql,
}) => {
  const { t } = useTranslation('sandboxDeployment');
  const { t: tErrors } = useTranslation('errors');
  const lineCount = (ddlCode.match(/\n/g) || []).length + 1;

  return (
    <div
      className="flex flex-col overflow-hidden rounded-2xl border border-slate-800 bg-[#090d16] shadow-xl shadow-slate-950/20"
      style={{ flex: 7 }}
    >
      <DdlActionsBar
        dialect={dialect}
        onDialectChange={onDialectChange}
        isGenerating={isGenerating}
        isDownloadDisabled={isDownloadDisabled}
        onFormat={onFormat}
        onCopy={onCopy}
        onDownloadDoc={onDownloadDoc}
        onDownloadSql={onDownloadSql}
      />

      {/* Dải báo lỗi khi Backend không sinh được mã DDL */}
      {errorCode && (
        <div className="flex items-start gap-2 px-4 py-2.5 bg-rose-500/10 border-b border-rose-500/30 text-[11px] text-rose-300">
          <AlertTriangle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
          <span>{tErrors(errorCode, { defaultValue: tErrors('UNKNOWN_ERROR') })}</span>
        </div>
      )}

      {/* Dải cảnh báo tương thích khi chuyển đổi sang dialect đích */}
      {warnings.length > 0 && (
        <div className="px-4 py-2.5 bg-amber-500/10 border-b border-amber-500/30 text-[11px] text-amber-300">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{t('warnings.title', { dialect: t(`dialect.${dialect}`) })}</span>
          </div>
          <ul className="mt-1 ml-5 list-disc space-y-0.5 text-amber-200/90">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-1 relative overflow-hidden bg-[#090d16] text-slate-100 font-mono">
        {/* Line Numbers Column */}
        <div className="w-12 bg-slate-950/80 border-r border-slate-800/80 py-4 text-right pr-2 text-[12.5px] text-slate-600 select-none leading-relaxed font-mono">
          {Array.from({ length: Math.max(lineCount, 20) }).map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        {/* SQL Code Textarea */}
        <textarea
          className="flex-1 border-none outline-none resize-none font-mono dark-scrollbar bg-transparent text-sky-300 text-[13px] leading-relaxed p-4 whitespace-pre selection:bg-sky-500/30 selection:text-sky-100"
          spellCheck={false}
          value={ddlCode}
          onChange={(e) => onChange(e.target.value)}
        />

        {/* Lớp phủ trạng thái đang sinh mã DDL */}
        {isGenerating && (
          <div className="absolute inset-0 flex items-center justify-center gap-2 bg-[#090d16]/80 text-[12px] text-sky-300">
            <Loader2 className="w-4 h-4 animate-spin" />
            {t('ddl_editor.loading')}
          </div>
        )}
      </div>

      {/* Editor Footer */}
      <div className="px-4 py-1.5 bg-slate-950/90 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-500 font-mono">
        <span>SQL Script • Lines: {lineCount} • UTF-8</span>
        <span>{t('ddl_editor.footer_meta', { schemaName, tableCount, revision })}</span>
      </div>
    </div>
  );
};
