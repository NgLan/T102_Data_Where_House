/**
 * Presentation Component: Cột phải Step 3 - Sandbox Config + Terminal
 * Glassmorphic panel với Host config, Deploy actions & ExecutionTerminal
 */

import {
  CheckCircle2,
  Database,
  KeyRound,
  Loader2,
  Lock,
  Play,
  PlugZap,
  Rocket,
  Save,
  Server,
  Terminal,
  User,
  XCircle,
} from 'lucide-react';
import type { ReactNode } from 'react';
import type { SandboxDbType, TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { ExecutionTerminal } from './ExecutionTerminal';

export interface SandboxConfigCardProps {
  dbType: SandboxDbType;
  onDbTypeChange: (value: SandboxDbType) => void;
  host: string;
  onHostChange: (value: string) => void;
  port: number;
  onPortChange: (value: number) => void;
  databaseName: string;
  onDatabaseNameChange: (value: string) => void;
  username: string;
  onUsernameChange: (value: string) => void;
  password?: string;
  onPasswordChange?: (value: string) => void;
  schemaName?: string;
  onSchemaNameChange?: (value: string) => void;

  isTestingConnection: boolean;
  connectionStatus: 'idle' | 'success' | 'error';
  connectionMessage?: string;
  onTestConnection: () => void;

  isSavingConfig: boolean;
  isLoading: boolean;
  isProjectReady: boolean;
  onSaveConfig: () => void;

  logs: TerminalLogEntryDto[];
  isDeploying: boolean;
  onDeploy: () => void;
}

/** Hiển thị thiết lập cấu hình Sandbox DB (UC9.1), kiểm tra kết nối, thực thi DDL (UC9.2) & Terminal log.
 * @param props Props chứa state và callbacks của sandbox.
 * @returns Component giao diện SandboxConfigCard.
 */
export function SandboxConfigCard(props: SandboxConfigCardProps) {
  return (
    <section className="flex flex-[3] flex-col gap-3.5 rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm overflow-y-auto">
      <header className="border-b border-slate-100 pb-3">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-sm font-bold text-slate-900">
            <Rocket className="size-4 text-blue-600" />
            Cấu hình Sandbox Database (UC9.1)
          </h2>
          {props.connectionStatus === 'success' && (
            <span className="flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
              <CheckCircle2 className="size-3 text-emerald-600" />
              Kết nối OK
            </span>
          )}
          {props.connectionStatus === 'error' && (
            <span className="flex items-center gap-1 rounded-full border border-red-200 bg-red-50 px-2 py-0.5 text-[10px] font-bold text-red-700">
              <XCircle className="size-3 text-red-600" />
              Lỗi kết nối
            </span>
          )}
          {props.connectionStatus === 'idle' && (
            <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-bold text-slate-600">
              Sẵn sàng
            </span>
          )}
        </div>
        <p className="mt-0.5 text-xs text-slate-500">
          Thiết lập kết nối đến Cơ sở dữ liệu Sandbox để chạy thử nghiệm mã DDL.
        </p>
        {props.connectionMessage && (
          <p className="mt-1 text-xs text-slate-600" role="status">{props.connectionMessage}</p>
        )}
        {!props.isProjectReady && (
          <p className="mt-1 text-xs font-medium text-amber-700" role="alert">
            Hãy tạo project trước khi lưu cấu hình hoặc chạy DDL.
          </p>
        )}
      </header>

      {/* Form Cấu hình Sandbox DB */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="col-span-2 space-y-1">
          <label className="font-bold text-slate-700 flex items-center gap-1.5">
            <Database className="size-3.5 text-blue-600" />
            Loại CSDL (Database Engine)
          </label>
          <select
            value={props.dbType}
            onChange={(e) => props.onDbTypeChange(e.target.value as SandboxDbType)}
            className="w-full h-9 rounded-md border border-slate-200 bg-white px-3 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="POSTGRESQL">PostgreSQL Database</option>
          </select>
        </div>

        <ConfigField
          id="sandbox-host"
          icon={<Server className="size-3.5 text-slate-600" />}
          label="Host / Server IP"
          value={props.host}
          onChange={props.onHostChange}
        />

        <ConfigField
          id="sandbox-port"
          icon={<PlugZap className="size-3.5 text-slate-600" />}
          label="Port"
          type="number"
          value={String(props.port)}
          onChange={(v) => props.onPortChange(Number(v) || 5432)}
        />

        <ConfigField
          id="sandbox-db"
          icon={<Database className="size-3.5 text-slate-600" />}
          label="Database Name"
          value={props.databaseName}
          onChange={props.onDatabaseNameChange}
        />

        <ConfigField
          id="sandbox-schema"
          icon={<Lock className="size-3.5 text-slate-600" />}
          label="Schema Name"
          value={props.schemaName ?? 'public'}
          onChange={(v) => props.onSchemaNameChange?.(v)}
        />

        <ConfigField
          id="sandbox-user"
          icon={<User className="size-3.5 text-slate-600" />}
          label="Username"
          value={props.username}
          onChange={props.onUsernameChange}
        />

        <ConfigField
          id="sandbox-pass"
          icon={<KeyRound className="size-3.5 text-slate-600" />}
          label="Password"
          type="password"
          value={props.password ?? ''}
          onChange={(v) => props.onPasswordChange?.(v)}
        />
      </div>

      {/* Hành động Cấu hình & Test Connection */}
      <div className="flex gap-2 pt-1 border-t border-slate-100">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="flex-1 text-xs"
          disabled={props.isTestingConnection || props.isLoading || !props.isProjectReady}
          onClick={props.onTestConnection}
        >
          {props.isTestingConnection ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <PlugZap className="size-3.5 text-slate-700" />
          )}
          {props.isTestingConnection ? 'Đang thử kết nối...' : 'Kiểm tra kết nối'}
        </Button>

        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="flex-1 text-xs"
          disabled={props.isSavingConfig || props.isLoading || !props.isProjectReady}
          onClick={props.onSaveConfig}
        >
          {props.isSavingConfig ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <Save className="size-3.5 text-slate-700" />
          )}
          Lưu cấu hình DB
        </Button>
      </div>

      {/* Nút Thực thi DDL (UC9.2) */}
      <div className="pt-1">
        <Button
          type="button"
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs"
          disabled={props.isDeploying || props.isLoading || !props.isProjectReady}
          onClick={props.onDeploy}
        >
          {props.isDeploying ? (
            <Loader2 className="size-4 animate-spin mr-1.5" />
          ) : (
            <Play className="size-4 fill-white mr-1.5" />
          )}
          {props.isDeploying ? 'Đang thực thi DDL...' : 'Thực thi chạy thử DDL (UC9.2)'}
        </Button>
      </div>

      {/* Terminal Log Output */}
      <div className="flex min-h-[220px] flex-1 flex-col pt-1">
        <div className="mb-1.5 flex items-center justify-between text-xs font-bold text-slate-700">
          <span className="flex items-center gap-1.5">
            <Terminal className="size-3.5 text-slate-600" />
            Nhật ký thực thi CLI Terminal
          </span>
          <span className="font-mono text-[10px] font-normal text-slate-400">Sandbox Log v1.0</span>
        </div>
        <ExecutionTerminal logs={props.logs} />
      </div>
    </section>
  );
};

interface ConfigFieldProps {
  id: string;
  icon: ReactNode;
  label: string;
  value: string;
  type?: string;
  onChange: (value: string) => void;
}

function ConfigField({ id, icon, label, value, type = 'text', onChange }: ConfigFieldProps) {
  return (
    <label htmlFor={id} className="space-y-1 text-xs font-bold text-slate-700">
      <span className="flex items-center gap-1.5">{icon}{label}</span>
      <Input
        id={id}
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="font-mono h-8 text-xs"
      />
    </label>
  );
}
