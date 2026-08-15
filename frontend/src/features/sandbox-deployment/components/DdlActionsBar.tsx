/**
 * Presentation Component: Thanh công cụ DDL Editor
 * Dark IDE Toolbar gồm dropdown chọn Hệ quản trị CSDL (UC5.5) và các nút Format / Copy / Tải file
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Code2, Wand2, Copy, FileText, Download, Loader2, Database } from 'lucide-react';
import { SQL_DIALECT_OPTIONS, SqlDialect } from '../types/sandbox.types';

export interface DdlActionsBarProps {
  dialect: SqlDialect;
  onDialectChange: (dialect: SqlDialect) => void;
  isGenerating: boolean;
  isDownloadDisabled: boolean;
  onFormat: () => void;
  onCopy: () => void;
  onDownloadDoc: () => void;
  onDownloadSql: () => void;
}

export const DdlActionsBar: React.FC<DdlActionsBarProps> = ({
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

  return (
    <div className="flex flex-wrap justify-between items-center bg-slate-900/90 px-4 py-3 border-b border-slate-800/80 text-slate-200 gap-2">
      <div className="flex items-center gap-2 text-xs font-bold tracking-wide">
        <Code2 className="w-4 h-4 text-sky-400" />
        <span className="text-slate-100 uppercase">{t('ddl_editor.title')}</span>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
          {t('ddl_editor.badge_editable')}
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {/* Dropdown chọn Hệ quản trị CSDL đích — quyết định cú pháp DDL sinh ra */}
        <label className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span className="sr-only sm:not-sr-only">{t('dialect.label')}</span>
          <select
            value={dialect}
            onChange={(event) => onDialectChange(event.target.value as SqlDialect)}
            aria-label={t('dialect.label')}
            className="px-2.5 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 outline-none transition cursor-pointer focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
          >
            {SQL_DIALECT_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {t(`dialect.${option}`)}
              </option>
            ))}
          </select>
        </label>

        <button
          onClick={onFormat}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
        >
          <Wand2 className="w-3.5 h-3.5 text-amber-400" /> {t('actions.format')}
        </button>

        <button
          onClick={onCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
        >
          <Copy className="w-3.5 h-3.5 text-sky-400" /> {t('actions.copy')}
        </button>

        <button
          onClick={onDownloadDoc}
          disabled={isDownloadDisabled}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-sky-900/60 hover:bg-sky-800 text-sky-200 border border-sky-700/60 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <FileText className="w-3.5 h-3.5 text-sky-300" /> {t('actions.download_doc')}
        </button>

        <button
          onClick={onDownloadSql}
          disabled={isDownloadDisabled}
          className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-sm transition cursor-pointer border border-blue-400/30 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
          {isGenerating ? t('actions.downloading') : t('actions.download_sql')}
        </button>
      </div>
    </div>
  );
};
