// @vitest-environment jsdom

import type { ReactNode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ModelingDashboardScreen } from '@/features/modeling-dashboard/components/ModelingDashboardScreen';
import { ProjectInitScreen } from '@/features/project-init/components/ProjectInitScreen';
import { SandboxDeploymentScreen } from '@/features/sandbox-deployment/components/SandboxDeploymentScreen';

const mocks = vi.hoisted(() => ({ push: vi.fn(), analyzeProject: vi.fn() }));

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock('next/navigation', () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock('next/link', () => ({ default: ({ href, children }: { href: string; children: ReactNode }) => <a href={href}>{children}</a> }));
vi.mock('@/features/project-init/hooks/use-project-init', () => ({ useProjectInit: () => ({
  domain: 'ride', setDomain: vi.fn(), targetDialect: 'PostgreSQL', setTargetDialect: vi.fn(),
  businessDescription: '', setBusinessDescription: vi.fn(), isMaskingEnabled: true,
  setIsMaskingEnabled: vi.fn(), excelFileName: 'sample.xlsx', excelRows: [], isAnalyzing: false,
  handleLoadSampleData: vi.fn(), analyzeProject: mocks.analyzeProject,
}) }));
vi.mock('@/features/project-init/components/AnalyzeTriggerButton', () => ({ AnalyzeTriggerButton: ({ onAnalyze }: { onAnalyze: () => void }) => <button onClick={onAnalyze}>analyze</button> }));
vi.mock('@/features/project-init/components/ProjectInitCard', () => ({ ProjectInitCard: () => null }));
vi.mock('@/features/project-init/components/ExcelDragDrop', () => ({ ExcelDragDrop: () => null }));
vi.mock('@/features/project-init/components/ExcelDataGrid', () => ({ ExcelDataGrid: () => null }));
vi.mock('@/features/project-init/components/MaskingToggle', () => ({ MaskingToggle: () => null }));
vi.mock('@/features/modeling-dashboard/ai-insights/hooks/use-ai-insights', () => ({ useAiInsights: () => ({ isWidgetOpen: false, toggleWidget: vi.fn(), selectedTableFilter: 'ALL', setSelectedTableFilter: vi.fn(), insights: [], tableNames: [], totalCount: 0 }) }));
vi.mock('@/features/modeling-dashboard/modeling-workspace/components/ModelingWorkspace', () => ({
  ModelingWorkspace: () => (
    <div>
      {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
      <a href="/?step=project-init">BTN_RECONFIGURE</a>
      {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
      <a href="/?step=sandbox">BTN_RUN_SANDBOX</a>
    </div>
  ),
}));
vi.mock('@/features/modeling-dashboard/ai-insights/components/AIInsightsPanel', () => ({ AIInsightsPanel: () => null }));
vi.mock('@/features/sandbox-deployment/hooks/use-sandbox-deploy', () => ({ useSandboxDeploy: () => ({ ddlCode: '', setDdlCode: vi.fn(), hostConnection: '', setHostConnection: vi.fn(), databaseSchema: '', setDatabaseSchema: vi.fn(), logs: [], isDeploying: false, handleFormatDdl: vi.fn(), handleCopyDdl: vi.fn(), handleDownloadDdl: vi.fn(), handleDownloadDoc: vi.fn(), handleDeploySandbox: vi.fn(), handleGenerateTestData: vi.fn() }) }));
vi.mock('@/features/sandbox-deployment/components/DdlCodeEditor', () => ({ DdlCodeEditor: () => null }));
vi.mock('@/features/sandbox-deployment/components/SandboxConfigCard', () => ({ SandboxConfigCard: () => null }));

describe('workflow screen navigation', () => {
  beforeEach(() => { mocks.push.mockReset(); mocks.analyzeProject.mockResolvedValue(undefined); });

  it('chuyển Project Init sang Modeling sau phân tích', async () => {
    render(<ProjectInitScreen />);
    fireEvent.click(screen.getByRole('button', { name: 'analyze' }));
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith('/?step=modeling'));
  });

  it('công bố đúng liên kết của Modeling', () => {
    render(<ModelingDashboardScreen />);
    expect(screen.getByRole('link', { name: /BTN_RECONFIGURE/ })).toHaveAttribute('href', '/?step=project-init');
    expect(screen.getByRole('link', { name: /BTN_RUN_SANDBOX/ })).toHaveAttribute('href', '/?step=sandbox');
  });

  it('cho phép Sandbox quay lại Modeling', () => {
    render(<SandboxDeploymentScreen />);
    expect(screen.getByRole('link', { name: /BTN_BACK_TO_MODELING/ })).toHaveAttribute('href', '/?step=modeling');
  });
});
