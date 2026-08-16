'use client';

import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { SandboxDbType, StatementLogDto, TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { useAppNotification } from '@/common/hooks/use-app-notification';
import {
  executeSandboxDdlApi,
  getDataModelDdlApi,
  getSandboxConfigApi,
  saveSandboxConfigApi,
  testSandboxConnectionApi,
} from '../services/sandbox-api';
import { copyToClipboard, formatSql } from '../utils/ddl-formatter';
import { downloadTextFile } from '../utils/file-helpers';

/** Quản lý DDL sinh từ Data Model, cấu hình kết nối và log thực thi thật. */
export function useSandboxDeploy(projectId: string | null) {
  const { t } = useTranslation('sandbox-deployment');
  const { notifySuccess, notifyError } = useAppNotification();

  const [ddlCode, setDdlCode] = useState('');
  const [dbType, setDbType] = useState<SandboxDbType>('POSTGRESQL');
  const [host, setHost] = useState('localhost');
  const [port, setPort] = useState<number>(5432);
  const [databaseName, setDatabaseName] = useState('sandbox_db');
  const [username, setUsername] = useState('postgres');
  const [password, setPassword] = useState('');
  const [schemaName, setSchemaName] = useState('public');

  const [isLoading, setIsLoading] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [connectionMessage, setConnectionMessage] = useState('');
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [logs, setLogs] = useState<TerminalLogEntryDto[]>(() => [
    createLog(t('MSG_LOG_READY', 'Sẵn sàng chạy DDL trên Sandbox Database.'), 'info'),
  ]);

  const loadSandboxData = useCallback(async () => {
    if (!projectId) {
      setDdlCode('');
      setLogs((current) => [
        ...current,
        createLog('[WARN] Chưa có project hợp lệ. Hãy quay lại bước khởi tạo.', 'error'),
      ]);
      return;
    }
    setIsLoading(true);
    try {
      const [config, ddl] = await Promise.all([
        getSandboxConfigApi(projectId),
        getDataModelDdlApi(projectId),
      ]);
      setDdlCode(ddl.ddl);
      if (config) {
        setDbType(config.db_type);
        setHost(config.host);
        setPort(config.port);
        setDatabaseName(config.database_name);
        setUsername(config.username ?? 'postgres');
        setSchemaName(config.schema_name ?? 'public');
        setConnectionMessage('Đã tải cấu hình Sandbox đã lưu.');
      } else {
        setConnectionMessage('Project chưa có cấu hình Sandbox; hãy nhập và lưu cấu hình.');
      }
      setLogs((current) => [
        ...current,
        createLog(`[INFO] Đã sinh DDL PostgreSQL từ Data Model revision ${ddl.revision}.`, 'info'),
      ]);
    } catch (error) {
      const message = errorMessage(error, 'Không thể tải DDL hoặc cấu hình Sandbox.');
      setLogs((current) => [...current, createLog(`[ERROR] ${message}`, 'error')]);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => void loadSandboxData(), 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadSandboxData]);

  const handleFormatDdl = () => setDdlCode((current) => formatSql(current));

  const handleCopyDdl = async (): Promise<void> => {
    if (!await copyToClipboard(ddlCode)) return;
    notifySuccess('MSG_DDL_COPIED');
  };

  const handleDownloadDdl = () => downloadTextFile('dwh_schema_ddl.sql', ddlCode, 'text/plain');

  const handleDownloadDoc = () => {
    const content = `# ${t('TXT_EDITOR_TITLE', 'Mô tả DDL Sandbox')}\n\n## ${databaseName}\n\n\`\`\`sql\n${ddlCode}\n\`\`\`\n`;
    downloadTextFile('schema_documentation.md', content, 'text/markdown');
  };

  const hasValidConfig = (): boolean => {
    const valid = Boolean(host.trim() && databaseName.trim() && port >= 1 && port <= 65535);
    if (!valid) notifyError('MSG_VALIDATION_ERROR');
    return valid;
  };

  const handleTestConnection = async () => {
    if (!projectId || !hasValidConfig()) return;
    setIsTestingConnection(true);
    setConnectionStatus('idle');
    setLogs((current) => [
      ...current,
      createLog(`[INFO] Đang kết nối tới ${host}:${port}/${databaseName}...`, 'info'),
    ]);
    try {
      const response = await testSandboxConnectionApi({
        db_type: dbType,
        host,
        port,
        database_name: databaseName,
        username,
        password,
        schema_name: schemaName,
      });
      setConnectionStatus(response.success ? 'success' : 'error');
      setConnectionMessage(response.message);
      setLogs((current) => [
        ...current,
        createLog(
          `[${response.success ? 'SUCCESS' : 'ERROR'}] ${response.message} (${response.latency_ms ?? 0}ms)`,
          response.success ? 'success' : 'error'
        ),
      ]);
      if (response.success) notifySuccess('MSG_ACTION_COMPLETED');
      else notifyError('MSG_ACTION_FAILED');
    } catch (error) {
      const message = errorMessage(error, 'Không thể thử kết nối đến DB Sandbox.');
      setConnectionStatus('error');
      setConnectionMessage(message);
      setLogs((current) => [...current, createLog(`[ERROR] ${message}`, 'error')]);
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!projectId || !hasValidConfig()) return;
    setIsSavingConfig(true);
    try {
      await saveSandboxConfigApi(projectId, {
        db_type: dbType,
        host,
        port,
        database_name: databaseName,
        username,
        password,
        schema_name: schemaName,
      });
      setPassword('');
      setLogs((current) => [...current, createLog('[SUCCESS] Đã lưu cấu hình Sandbox.', 'success')]);
      notifySuccess('MSG_ACTION_COMPLETED');
    } catch (error) {
      const message = errorMessage(error, 'Không thể lưu cấu hình Sandbox.');
      setLogs((current) => [...current, createLog(`[ERROR] ${message}`, 'error')]);
      notifyError('MSG_ACTION_FAILED');
    } finally {
      setIsSavingConfig(false);
    }
  };

  const handleDeploySandbox = async () => {
    if (!projectId || !ddlCode.trim()) {
      notifyError('MSG_VALIDATION_ERROR');
      return;
    }
    setIsDeploying(true);
    setLogs((current) => [
      ...current,
      createLog(`[INFO] Bắt đầu thực thi DDL trên ${host}:${port}/${databaseName}...`, 'info'),
    ]);
    try {
      const response = await executeSandboxDdlApi(projectId, ddlCode);
      const statementLogs: TerminalLogEntryDto[] = response.logs.map(mapStatementLog);
      statementLogs.push(
        createLog(
          `[SUMMARY] ${response.succeeded_statements}/${response.executed_statements} câu lệnh thành công (${response.total_duration_ms}ms).`,
          response.success ? 'success' : 'error'
        )
      );
      setLogs((current) => [...current, ...statementLogs]);
      if (response.success) notifySuccess('MSG_SANDBOX_EXECUTION_SUCCESS');
      else notifyError('MSG_SANDBOX_EXECUTION_FAILED');
    } catch (error) {
      const message = errorMessage(error, 'Không thể thực thi DDL trên Sandbox.');
      setLogs((current) => [...current, createLog(`[ERROR] ${message}`, 'error')]);
      notifyError('MSG_SANDBOX_EXECUTION_FAILED');
    } finally {
      setIsDeploying(false);
    }
  };

  return {
    ddlCode,
    setDdlCode,
    dbType,
    setDbType,
    host,
    setHost,
    port,
    setPort,
    databaseName,
    setDatabaseName,
    username,
    setUsername,
    password,
    setPassword,
    schemaName,
    setSchemaName,
    isLoading,
    isTestingConnection,
    connectionStatus,
    connectionMessage,
    isSavingConfig,
    isDeploying,
    logs,
    handleFormatDdl,
    handleCopyDdl,
    handleDownloadDdl,
    handleDownloadDoc,
    handleTestConnection,
    handleSaveConfig,
    handleDeploySandbox,
  };
}

function mapStatementLog(log: StatementLogDto): TerminalLogEntryDto {
  return {
    timestamp: log.timestamp || new Date().toLocaleTimeString(),
    message: log.is_success
      ? `[OK ${log.execution_time_ms}ms] ${log.statement.split('\n')[0]}`
      : `[FAIL] ${log.statement.split('\n')[0]} - ${log.error_detail || 'Unknown error'}`,
    type: log.is_success ? 'success' : 'error',
  };
}

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}

function createLog(message: string, type: TerminalLogEntryDto['type']): TerminalLogEntryDto {
  return { timestamp: new Date().toLocaleTimeString(), message, type };
}
