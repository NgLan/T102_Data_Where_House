/**
 * Presentation Component: DDL Code Editor (Cột trái Step 3)
 * Full-height SQL Editor với DdlActionsBar, line numbers & code syntax colors
 */

import React from 'react';
import { DdlActionsBar, DdlActionsBarProps } from './DdlActionsBar';

export interface DdlCodeEditorProps extends DdlActionsBarProps {
  ddlCode: string;
  onChange: (value: string) => void;
}

export const DdlCodeEditor: React.FC<DdlCodeEditorProps> = ({
  ddlCode,
  onChange,
  onFormat,
  onCopy,
  onDownloadDoc,
  onDownloadSql,
}) => {
  const lineCount = (ddlCode.match(/\n/g) || []).length + 1;

  return (
    <div
      className="flex flex-col overflow-hidden rounded-2xl border border-slate-800 bg-[#090d16] shadow-xl shadow-slate-950/20"
      style={{ flex: 7 }}
    >
      <DdlActionsBar
        onFormat={onFormat}
        onCopy={onCopy}
        onDownloadDoc={onDownloadDoc}
        onDownloadSql={onDownloadSql}
      />

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
      </div>

      {/* Editor Footer */}
      <div className="px-4 py-1.5 bg-slate-950/90 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-500 font-mono">
        <span>SQL Script • Lines: {lineCount} • UTF-8</span>
        <span>Target: PostgreSQL Dialect</span>
      </div>
    </div>
  );
};

