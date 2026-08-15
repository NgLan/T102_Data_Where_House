'use client';

import { Database, FlaskConical, Loader2, Rocket, Server, Terminal } from 'lucide-react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import type { TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { ExecutionTerminal } from './ExecutionTerminal';

export interface SandboxConfigCardProps {
  host: string;
  onHostChange: (value: string) => void;
  database: string;
  onDatabaseChange: (value: string) => void;
  logs: TerminalLogEntryDto[];
  isDeploying: boolean;
  onDeploy: () => void;
  onGenerateTestData: () => void;
}

/** Hiển thị cấu hình, action và terminal của sandbox.
 * @param props State cấu hình cùng các callback triển khai.
 * @returns Panel sandbox dùng primitive shadcn.
 */
export function SandboxConfigCard(props: SandboxConfigCardProps) {
  const { t } = useTranslation('sandbox-deployment');
  return (
    <section className="flex flex-[3] flex-col gap-3.5 rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
      <header><div className="flex items-center justify-between"><h2 className="flex items-center gap-2 text-sm font-bold text-slate-900"><Rocket className="size-4 text-blue-600" />{t('TXT_SANDBOX_TITLE')}</h2><span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">{t('TXT_READY')}</span></div><p className="mt-0.5 text-xs text-slate-400">{t('TXT_SANDBOX_DESCRIPTION')}</p></header>
      <ConfigField id="sandbox-host" icon={<Server />} label={t('HOST_LABEL')} value={props.host} onChange={props.onHostChange} />
      <ConfigField id="sandbox-database" icon={<Database />} label={t('DATABASE_LABEL')} value={props.database} onChange={props.onDatabaseChange} />
      <div className="space-y-2 pt-1">
        <Button type="button" className="w-full" disabled={props.isDeploying} onClick={props.onDeploy}>{props.isDeploying ? <Loader2 className="animate-spin" /> : <Rocket />}{props.isDeploying ? t('MSG_DEPLOYING') : t('BTN_DEPLOY')}</Button>
        <Button type="button" className="w-full" variant="outline" onClick={props.onGenerateTestData}><FlaskConical />{t('BTN_GENERATE_TEST_DATA')}</Button>
      </div>
      <div className="flex min-h-[220px] flex-1 flex-col pt-1">
        <div className="mb-1.5 flex items-center justify-between text-xs font-bold text-slate-700"><span className="flex items-center gap-1.5"><Terminal className="size-3.5 text-slate-600" />{t('TXT_TERMINAL_LOG')}</span><span className="font-mono text-[10px] font-normal text-slate-400">{t('TXT_TERMINAL_VERSION')}</span></div>
        <ExecutionTerminal logs={props.logs} />
      </div>
    </section>
  );
}

interface ConfigFieldProps {
  id: string;
  icon: ReactNode;
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function ConfigField({ id, icon, label, value, onChange }: ConfigFieldProps) {
  return <label htmlFor={id} className="space-y-1 text-xs font-bold text-slate-700"><span className="flex items-center gap-1.5 [&_svg]:size-3.5">{icon}{label}</span><Input id={id} value={value} onChange={(event) => onChange(event.target.value)} className="font-mono" /></label>;
}
