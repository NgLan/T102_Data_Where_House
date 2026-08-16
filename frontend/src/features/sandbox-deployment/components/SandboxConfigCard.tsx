/**
 * Presentation Component: Cột phải Step 3 - Sandbox Config + Terminal
 * Glassmorphic panel với Host config, Deploy actions & ExecutionTerminal
 */

import React from 'react';
import { ExecutionTerminal } from './ExecutionTerminal';
import { TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { Rocket, Server, Database, FlaskConical, Terminal, CheckCircle2, Loader2 } from 'lucide-react';

export interface SandboxConfigCardProps {
  host: string;
  onHostChange: (val: string) => void;
  database: string;
  onDatabaseChange: (val: string) => void;
  logs: TerminalLogEntryDto[];
  isDeploying: boolean;
  onDeploy: () => void;
  onGenerateTestData: () => void;
}

export const SandboxConfigCard: React.FC<SandboxConfigCardProps> = ({
  host,
  onHostChange,
  database,
  onDatabaseChange,
  logs,
  isDeploying,
  onDeploy,
  onGenerateTestData,
}) => {
  return (
    <div
      className="flex flex-col bg-white border border-slate-200/90 rounded-2xl p-5 gap-3.5 shadow-sm"
      style={{ flex: 3 }}
    >
      {/* Panel Header */}
      <div>
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 m-0">
            <Rocket className="w-4 h-4 text-blue-600" /> Thử nghiệm Môi trường Sandbox
          </h3>
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Ready
          </span>
        </div>
        <p className="text-xs text-slate-400 m-0 mt-0.5">
          Tự động tạo schema thử nghiệm để validate DDL & sinh dữ liệu mẫu test query
        </p>
      </div>

      {/* Host Connection Input */}
      <div>
        <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1">
          <Server className="w-3.5 h-3.5 text-indigo-600" /> Host Connection
        </label>
        <input
          type="text"
          value={host}
          onChange={(e) => onHostChange(e.target.value)}
          className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-slate-50/50 font-mono text-slate-800 outline-none focus:border-blue-500 focus:bg-white transition"
        />
      </div>

      {/* Database & Target Schema Input */}
      <div>
        <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1">
          <Database className="w-3.5 h-3.5 text-violet-600" /> Database & Target Schema
        </label>
        <input
          type="text"
          value={database}
          onChange={(e) => onDatabaseChange(e.target.value)}
          className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-slate-50/50 font-mono text-slate-800 outline-none focus:border-blue-500 focus:bg-white transition"
        />
      </div>

      {/* Action Buttons */}
      <div className="space-y-2 pt-1">
        <button
          onClick={onDeploy}
          disabled={isDeploying}
          className="w-full py-2.5 px-4 text-xs font-bold rounded-xl border-none text-white cursor-pointer transition-all duration-200 disabled:opacity-60 flex items-center justify-center gap-2 glow-btn-primary shadow-md shadow-blue-500/20"
        >
          {isDeploying ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Đang Deploy Sandbox Schema...</span>
            </>
          ) : (
            <>
              <Rocket className="w-4 h-4" />
              <span>Exec DDL & Deploy Sandbox</span>
            </>
          )}
        </button>

        <button
          onClick={onGenerateTestData}
          className="w-full py-2 px-3 text-xs font-semibold rounded-xl border border-slate-200 text-slate-700 bg-slate-50 hover:bg-slate-100 cursor-pointer transition-all flex items-center justify-center gap-1.5"
        >
          <FlaskConical className="w-3.5 h-3.5 text-emerald-600" />
          <span>Generates Test Mock Data (100 rows)</span>
        </button>
      </div>

      {/* Terminal Output Log Container */}
      <div className="flex flex-col flex-1 min-h-[220px] pt-1">
        <label className="flex items-center justify-between text-xs font-bold text-slate-700 mb-1.5">
          <span className="flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-slate-600" /> Terminal Output Log:
          </span>
          <span className="text-[10px] font-mono text-slate-400 font-normal">Console v1.2</span>
        </label>
        <ExecutionTerminal logs={logs} />
      </div>
    </div>
  );
};

