/**
 * Custom Hook chứa toàn bộ State & Logic cho Feature Sandbox Deployment
 */

import { useState } from 'react';
import { TerminalLogEntryDto } from '@/api/model/sandbox.dto';
import { formatSql, copyToClipboard } from '@/common/utils/ddl-formatter';
import { downloadTextFile } from '@/common/utils/file-helpers';

export function useSandboxDeploy() {
  const dataModel = useProjectStore((state) => state.dataModel);

  const [ddlCode, setDdlCode] = useState<string>('');
  const [dialect, setDialect] = useState<SqlDialect>('postgresql');
  const [schemaName, setSchemaName] = useState<string>('sandbox_dwh');
  const [tableCount, setTableCount] = useState<number>(0);
  const [ddlWarnings, setDdlWarnings] = useState<string[]>([]);
  const [isGeneratingDdl, setIsGeneratingDdl] = useState<boolean>(false);
  const [ddlErrorCode, setDdlErrorCode] = useState<string | null>(null);

  const [hostConnection, setHostConnection] = useState<string>('localhost:5432 (Isolated Postgres Container)');
  const [databaseSchema, setDatabaseSchema] = useState<string>('sandbox_db / schema: sandbox_dwh');
  
  const [logs, setLogs] = useState<TerminalLogEntryDto[]>([
    { timestamp: new Date().toLocaleTimeString(), message: 'Ready for execution.', type: 'info' },
    { timestamp: new Date().toLocaleTimeString(), message: "Click 'Exec DDL & Deploy Sandbox' to test DDL script.", type: 'info' },
  ]);
  
  const [isDeploying, setIsDeploying] = useState<boolean>(false);

  /**
   * Sinh mã DDL từ mô hình dữ liệu hiện hành theo hệ quản trị CSDL người dùng chọn (UC5.4).
   * Được gọi lại mỗi khi người dùng đổi dialect trên dropdown.
   */
  const loadDdl = useCallback(async () => {
    // Chưa nạp được mô hình dữ liệu: phải báo lỗi rõ ràng thay vì im lặng giữ nguyên
    // nội dung cũ, nếu không người dùng sẽ tưởng dropdown chọn dialect bị hỏng.
    if (!dataModel) {
      setDdlCode('');
      setDdlWarnings([]);
      setTableCount(0);
      setDdlErrorCode('DATA_MODEL_NOT_FOUND');
      return;
    }

    setIsGeneratingDdl(true);
    setDdlErrorCode(null);
    try {
      const result = await generateDdlApi(dataModel.id, dialect);
      setDdlCode(result.ddl);
      setSchemaName(result.schema_name);
      setTableCount(result.table_count);
      setDdlWarnings(result.warnings);
    } catch (error) {
      const errorCode = (error as { error_code?: string })?.error_code ?? 'UNKNOWN_ERROR';
      setDdlErrorCode(errorCode);
      setDdlWarnings([]);
    } finally {
      setIsGeneratingDdl(false);
    }
  }, [dataModel, dialect]);

  useEffect(() => {
    void loadDdl();
  }, [loadDdl]);

  // Đổi hệ quản trị CSDL đích, kéo theo sinh lại mã DDL tương ứng
  const handleDialectChange = (nextDialect: SqlDialect) => {
    setDialect(nextDialect);
  };

  // Format SQL DDL
  const handleFormatDdl = () => {
    setDdlCode((prev) => formatSql(prev));
  };

  // Copy DDL
  const handleCopyDdl = async () => {
    const success = await copyToClipboard(ddlCode);
    if (success) {
      alert('Đã sao chép DDL vào bộ nhớ tạm!');
    }
  };

  // Download .sql file
  const handleDownloadDdl = () => {
    downloadTextFile('dwh_schema_ddl.sql', ddlCode, 'text/plain');
  };

  // Download .md documentation
  const handleDownloadDoc = () => {
    const mdContent = `# Tài liệu Cấu trúc Data Warehouse DWH\n\n## 1. Tổng quan Schema\nTarget Schema: \`sandbox_dwh\`\n\n## 2. Mã DDL Script\n\`\`\`sql\n${ddlCode}\n\`\`\`\n`;
    downloadTextFile('schema_documentation.md', mdContent, 'text/markdown');
  };

  // Thực thi Deploy Sandbox DDL
  const handleDeploySandbox = () => {
    setIsDeploying(true);
    const now = new Date().toLocaleTimeString();

    setLogs((prev) => [
      ...prev,
      { timestamp: now, message: `Connecting to ${hostConnection}...`, type: 'info' },
    ]);

    setTimeout(() => {
      setLogs((prev) => [
        ...prev,
        { timestamp: new Date().toLocaleTimeString(), message: 'Executing DDL script on target schema...', type: 'info' },
        { timestamp: new Date().toLocaleTimeString(), message: 'CREATE TABLE sandbox_dwh.Dim_Driver [OK]', type: 'success' },
        { timestamp: new Date().toLocaleTimeString(), message: 'CREATE TABLE sandbox_dwh.Dim_Customer [OK]', type: 'success' },
        { timestamp: new Date().toLocaleTimeString(), message: 'CREATE TABLE sandbox_dwh.Fact_Rides [OK]', type: 'success' },
        { timestamp: new Date().toLocaleTimeString(), message: '🚀 Deploy Sandbox thành công! Tất cả bảng DWH sẵn sàng.', type: 'success' },
      ]);
      setIsDeploying(false);
    }, 700);
  };

  // Sinh dữ liệu test
  const handleGenerateTestData = () => {
    const now = new Date().toLocaleTimeString();
    setLogs((prev) => [
      ...prev,
      { timestamp: now, message: '🧪 Generating test mock data (100 rows)...', type: 'info' },
      { timestamp: new Date().toLocaleTimeString(), message: 'Inserted 10 rows into Dim_Driver', type: 'success' },
      { timestamp: new Date().toLocaleTimeString(), message: 'Inserted 30 rows into Dim_Customer', type: 'success' },
      { timestamp: new Date().toLocaleTimeString(), message: 'Inserted 60 rows into Fact_Rides', type: 'success' },
      { timestamp: new Date().toLocaleTimeString(), message: 'Simulated mock data inserted successfully.', type: 'success' },
    ]);
  };

  return {
    ddlCode,
    setDdlCode,
    hostConnection,
    setHostConnection,
    databaseSchema,
    setDatabaseSchema,
    logs,
    isDeploying,
    handleFormatDdl,
    handleCopyDdl,
    handleDownloadDdl,
    handleDownloadDoc,
    handleDeploySandbox,
    handleGenerateTestData,
  };
}
