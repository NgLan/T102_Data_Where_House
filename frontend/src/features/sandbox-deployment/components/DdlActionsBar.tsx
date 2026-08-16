/**
 * Presentation Component: Thanh công cụ DDL Editor
 * Dark IDE Toolbar với các nút thao tác nhanh (Format, Copy, Download)
 */

import React from 'react';
import { Code2, Wand2, Copy, FileText, Download } from 'lucide-react';

export interface DdlActionsBarProps {
  onFormat: () => void;
  onCopy: () => void;
  onDownloadDoc: () => void;
  onDownloadSql: () => void;
}

export const DdlActionsBar: React.FC<DdlActionsBarProps> = ({
  onFormat,
  onCopy,
  onDownloadDoc,
  onDownloadSql,
}) => {
  return (
    <div className="flex flex-wrap justify-between items-center bg-slate-900/90 px-4 py-3 border-b border-slate-800/80 text-slate-200 gap-2">
      <div className="flex items-center gap-2 text-xs font-bold tracking-wide">
        <Code2 className="w-4 h-4 text-sky-400" />
        <span className="text-slate-100">POSTGRESQL DWH DDL SCRIPT</span>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
          Editable
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onFormat}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
        >
          <Wand2 className="w-3.5 h-3.5 text-amber-400" /> Format SQL
        </button>

        <button
          onClick={onCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
        >
          <Copy className="w-3.5 h-3.5 text-sky-400" /> Copy DDL
        </button>

        <button
          onClick={onDownloadDoc}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-sky-900/60 hover:bg-sky-800 text-sky-200 border border-sky-700/60 transition cursor-pointer"
        >
          <FileText className="w-3.5 h-3.5 text-sky-300" /> Tải Data Doc (.md)
        </button>

        <button
          onClick={onDownloadSql}
          className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-sm transition cursor-pointer border border-blue-400/30"
        >
          <Download className="w-3.5 h-3.5" /> Tải file .sql
        </button>
      </div>
    </div>
  );
};

