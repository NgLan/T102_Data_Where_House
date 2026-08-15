'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { useAppNotification } from '@/common/hooks/use-app-notification';
import { copyToClipboard, formatSql } from '../utils/ddl-formatter';
import { DEFAULT_DDL } from '../utils/default-ddl';
import { downloadTextFile } from '../utils/file-helpers';

/** Quản lý DDL source, cấu hình và log mô phỏng của sandbox.
 * @returns State cùng các action chỉnh sửa, tải file và triển khai.
 * @remarks Tác vụ triển khai hiện là mô phỏng client-side và thêm log sau 700 ms.
 */
export function useSandboxDeploy() {
  const { t } = useTranslation('sandbox-deployment');
  const { notifySuccess } = useAppNotification();
  const [ddlCode, setDdlCode] = useState(DEFAULT_DDL);
  const [hostConnection, setHostConnection] = useState('localhost:5432');
  const [databaseSchema, setDatabaseSchema] = useState('sandbox_db / sandbox_dwh');
  const [logs, setLogs] = useState<TerminalLogEntryDto[]>(() => [createLog(t('MSG_LOG_READY'), 'info')]);
  const [isDeploying, setIsDeploying] = useState(false);

  const handleFormatDdl = () => setDdlCode((current) => formatSql(current));
  const handleCopyDdl = async (): Promise<void> => {
    if (!await copyToClipboard(ddlCode)) return;
    notifySuccess('MSG_DDL_COPIED');
  };
  const handleDownloadDdl = () => downloadTextFile('dwh_schema_ddl.sql', ddlCode, 'text/plain');
  const handleDownloadDoc = () => {
    const content = `# ${t('TXT_EDITOR_TITLE')}\n\n## sandbox_dwh\n\n\`\`\`sql\n${ddlCode}\n\`\`\`\n`;
    downloadTextFile('schema_documentation.md', content, 'text/markdown');
  };
  const handleDeploySandbox = () => {
    setIsDeploying(true);
    setLogs((current) => [...current, createLog(t('MSG_LOG_CONNECTING', { host: hostConnection }), 'info')]);
    window.setTimeout(() => {
      setLogs((current) => [...current, ...deploymentLogs(t('MSG_LOG_EXECUTING'), t('MSG_LOG_DEPLOYED'))]);
      setIsDeploying(false);
    }, 700);
  };
  const handleGenerateTestData = () => setLogs((current) => [
    ...current, createLog(t('MSG_LOG_GENERATING', { count: 100 }), 'info'),
    createLog(t('MSG_LOG_GENERATED'), 'success'),
  ]);

  return {
    ddlCode, setDdlCode, hostConnection, setHostConnection, databaseSchema, setDatabaseSchema,
    logs, isDeploying, handleFormatDdl, handleCopyDdl, handleDownloadDdl, handleDownloadDoc,
    handleDeploySandbox, handleGenerateTestData,
  };
}

function deploymentLogs(executingMessage: string, deployedMessage: string): TerminalLogEntryDto[] {
  return [
    createLog(executingMessage, 'info'),
    createLog('CREATE TABLE sandbox_dwh.Dim_Driver [OK]', 'success'),
    createLog('CREATE TABLE sandbox_dwh.Dim_Customer [OK]', 'success'),
    createLog('CREATE TABLE sandbox_dwh.Fact_Rides [OK]', 'success'),
    createLog(deployedMessage, 'success'),
  ];
}

function createLog(message: string, type: TerminalLogEntryDto['type']): TerminalLogEntryDto {
  return { timestamp: new Date().toLocaleTimeString(), message, type };
}
