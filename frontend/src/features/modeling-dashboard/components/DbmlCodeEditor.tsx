/**
 * Presentation Component: DBML Code Editor (dbdiagram.io DSL Text)
 * Sleek Dark IDE với Line Numbers, Live Sync Indicator & Quick Actions
 */

import React from 'react';
import { Code, Copy, Check, RefreshCw } from 'lucide-react';

export interface DbmlCodeEditorProps {
  code: string;
  onChange: (val: string) => void;
}

export const DbmlCodeEditor: React.FC<DbmlCodeEditorProps> = ({ code, onChange }) => {
  const [copied, setCopied] = React.useState(false);
  const lineCount = (code.match(/\n/g) || []).length + 1;

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="flex flex-col font-mono text-slate-300 rounded-2xl border border-slate-800 bg-[#090d16] overflow-hidden shadow-lg shadow-slate-950/20"
      style={{ flex: 4 }}
    >
      {/* Header Toolbar */}
      <div className="flex justify-between items-center px-4 py-2.5 bg-slate-900/90 border-b border-slate-800/80 text-xs font-semibold">
        <div className="flex items-center gap-2 text-slate-200">
          <Code className="w-4 h-4 text-sky-400" />
          <span className="font-bold tracking-wide">DBML EDITOR</span>
          <span className="text-[10px] bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded-full font-mono">
            dbdiagram DSL
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-sans">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Live Sync
          </span>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-sans transition cursor-pointer border border-slate-700"
            title="Copy DBML Code"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Editor Body with Line Numbers */}
      <div className="flex flex-1 relative overflow-hidden" style={{ minHeight: '440px' }}>
        {/* Line Numbers Column */}
        <div className="w-10 bg-slate-950/70 border-r border-slate-800/60 py-3 text-right pr-2 text-[12px] font-mono text-slate-600 select-none leading-relaxed">
          {Array.from({ length: Math.max(lineCount, 16) }).map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        {/* Code Textarea */}
        <textarea
          className="flex-1 bg-transparent border-none text-sky-300 font-mono text-[12.5px] leading-relaxed p-3 outline-none resize-none dark-scrollbar selection:bg-sky-500/30 selection:text-sky-100"
          spellCheck={false}
          value={code}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>

      {/* Footer Info Bar */}
      <div className="px-4 py-1.5 bg-slate-950/90 border-t border-slate-800/60 flex justify-between items-center text-[10px] text-slate-500 font-mono">
        <span>Lines: {lineCount} | Chars: {code.length}</span>
        <span>DBML v2.1 • UTF-8</span>
      </div>
    </div>
  );
};

