'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';
import { MainLayout } from '@/common/components/layout/MainLayout';
import { createWorkflowHref } from '@/common/routing/workflow-routing';
import { useSandboxDeploy } from '../hooks/use-sandbox-deploy';
import { DdlCodeEditor } from './DdlCodeEditor';
import { SandboxConfigCard } from './SandboxConfigCard';

/** Điều phối màn hình chỉnh DDL và triển khai sandbox.
 * @returns Feature screen gồm editor, cấu hình và terminal thực thi.
 */
export interface SandboxDeploymentScreenProps {
  projectId?: string | null;
}

export function SandboxDeploymentScreen({ projectId = null }: SandboxDeploymentScreenProps) {
  const { t } = useTranslation('sandbox-deployment');
  const sandbox = useSandboxDeploy(projectId);

  return (
    <MainLayout>
      <div className="flex w-full flex-1 flex-col space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <header className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/80 bg-white/80 px-5 py-3 shadow-xs backdrop-blur-md">
          <div>
            <h1 className="text-lg font-extrabold tracking-tight text-slate-900">{t('TXT_SCREEN_TITLE', 'Quản lý & Chạy thử DDL Sandbox')}</h1>
            <p className="text-xs text-slate-500">{t('TXT_SCREEN_SUBTITLE', 'Thiết lập cấu hình CSDL Sandbox (UC9.1) và thực thi chạy thử mã DDL (UC9.2)')}</p>
          </div>
          <Button asChild variant="outline">
            <Link href={createWorkflowHref('modeling', projectId)}>
              <ArrowLeft />
              {t('BTN_BACK_TO_MODELING', 'Quay lại Mô hình hóa')}
            </Link>
          </Button>
        </header>

        <div className="flex flex-1 flex-col gap-4 lg:min-h-[calc(100vh-170px)] lg:flex-row">
          <DdlCodeEditor
            ddlCode={sandbox.ddlCode}
            onChange={sandbox.setDdlCode}
            onFormat={sandbox.handleFormatDdl}
            onCopy={sandbox.handleCopyDdl}
            onDownloadDoc={sandbox.handleDownloadDoc}
            onDownloadSql={sandbox.handleDownloadDdl}
          />
          <SandboxConfigCard
            dbType={sandbox.dbType}
            onDbTypeChange={sandbox.setDbType}
            host={sandbox.host}
            onHostChange={sandbox.setHost}
            port={sandbox.port}
            onPortChange={sandbox.setPort}
            databaseName={sandbox.databaseName}
            onDatabaseNameChange={sandbox.setDatabaseName}
            username={sandbox.username}
            onUsernameChange={sandbox.setUsername}
            password={sandbox.password}
            onPasswordChange={sandbox.setPassword}
            schemaName={sandbox.schemaName}
            onSchemaNameChange={sandbox.setSchemaName}
            isTestingConnection={sandbox.isTestingConnection}
            connectionStatus={sandbox.connectionStatus}
            connectionMessage={sandbox.connectionMessage}
            onTestConnection={sandbox.handleTestConnection}
            isSavingConfig={sandbox.isSavingConfig}
            isLoading={sandbox.isLoading}
            isProjectReady={Boolean(projectId)}
            onSaveConfig={sandbox.handleSaveConfig}
            logs={sandbox.logs}
            isDeploying={sandbox.isDeploying}
            onDeploy={sandbox.handleDeploySandbox}
          />
        </div>
      </div>
    </MainLayout>
  );
}
