/**
 * Presentation Component: Terminal log box hiển thị kết quả thực thi Sandbox
 * Developer dark console với terminal window controls & color-coded logs
 */

import React from 'react';
import { TerminalLogEntryDto } from '@/api/model/sandbox.dto';

export interface ExecutionTerminalProps {
  logs: TerminalLogEntryDto[];
}

export const ExecutionTerminal: React.FC<ExecutionTerminalProps> = ({ logs }) => {
  return (
    <div className="flex flex-col flex-1 rounded-xl border border-slate-800 bg-[#090d16] overflow-hidden shadow-inner font-mono text-[11.5px] leading-relaxed">
      {/* Terminal Window Header Bar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-950/80 border-b border-slate-800/80 text-[10px] text-slate-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
        </div>
        <span className="font-mono text-slate-400">sandbox@sandbox-dwh:~</span>
      </div>

      {/* Terminal Logs Window */}
      <div className="flex-1 p-3 overflow-y-auto dark-scrollbar space-y-1" style={{ minHeight: '180px' }}>
        {logs.length === 0 ? (
          <div className="text-slate-500 space-y-1">
            <div className="flex items-center gap-1.5 text-emerald-400/90">
              <span className="text-slate-600">❯</span> Ready for DDL execution.
            </div>
            <div className="text-slate-500">
              <span className="text-slate-600">❯</span> Click &apos;Exec DDL &amp; Deploy Sandbox&apos; to validate DDL script.
            </div>
          </div>
        ) : (
          logs.map((log, index) => {
            const isError = log.type === 'error';
            const isSuccess = log.type === 'success';

            return (
              <div key={index} className="flex items-start gap-1.5 font-mono">
                <span className="text-slate-600 select-none">❯</span>
                <span className="text-slate-500 text-[10.5px]">[{log.timestamp}]</span>
                <span
                  className={
                    isError
                      ? 'text-rose-400 font-semibold'
                      : isSuccess
                      ? 'text-emerald-400 font-semibold'
                      : 'text-slate-300'
                  }
                >
                  {log.message}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

