// @vitest-environment jsdom

import type { ReactNode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ModelingDashboardScreen } from '@/features/modeling-dashboard/ModelingDashboardScreen';
import { ProjectInitScreen } from '@/features/project-init';
import { SandboxDeploymentScreen } from '@/features/sandbox-deployment';

const PROJECT_ID = '2f4a682b-78f5-4b3e-8b25-fc9ca3387df0';
const mocks = vi.hoisted(() => ({ push: vi.fn(), analyzeProject: vi.fn() }));

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock('next/navigation', () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock('next/link', () => ({ default: ({ href, children }: { href: string; children: ReactNode }) => <a href={href}>{children}</a> }));
vi.mock('@/features/project-init/project-details/hooks/use-project-details', () => ({ useProjectDetails: () => ({
  appendRequirement: vi.fn(), errors: {}, form: { name: 'Project', domain: 'ride', requirement: 'Requirement' },
  isLoading: false, isSaving: false, loadError: null, reload: vi.fn(), save: mocks.saveProject,
  updateField: vi.fn(),
}) }));
vi.mock('@/features/project-init/data-sources/hooks/use-data-sources', () => ({ useDataSources: () => ({
  canEdit: true, deleteSource: vi.fn(), isLoading: false, isMutating: false, loadError: null,
  reload: vi.fn(), sources: [], updateColumn: vi.fn(), uploadFiles: vi.fn(),
}) }));
vi.mock('@/features/project-init/data-sources/components/DataSourceSection', () => ({ DataSourceSection: () => null }));
vi.mock('@/features/project-init/project-details/components/ProjectDetailsForm', () => ({ ProjectDetailsForm: () => null }));
vi.mock('@/features/project-init/pii-guard/components/PiiGuardNotice', () => ({ PiiGuardNotice: () => null }));
vi.mock('@/features/modeling-dashboard/ai-insights/hooks/use-ai-insights', () => ({ useAiInsights: () => ({ isWidgetOpen: false, toggleWidget: vi.fn(), selectedTableFilter: 'ALL', setSelectedTableFilter: vi.fn(), insights: [], tableNames: [], totalCount: 0 }) }));
vi.mock('@/features/modeling-dashboard/modeling-workspace/components/ModelingWorkspace', () => ({
  ModelingWorkspace: ({ projectId }: { projectId: string }) => (
    <div>
      <a href={`/projects/${projectId}?step=project-init`}>BTN_RECONFIGURE</a>
      <a href={`/projects/${projectId}?step=sandbox`}>BTN_RUN_SANDBOX</a>
    </div>
  ),
}));
vi.mock('@/features/modeling-dashboard/ai-insights/components/AIInsightsPanel', () => ({ AIInsightsPanel: () => null }));
vi.mock('@/features/sandbox-deployment/hooks/use-sandbox-deploy', () => ({ useSandboxDeploy: () => ({ ddlCode: '', setDdlCode: vi.fn(), hostConnection: '', setHostConnection: vi.fn(), databaseSchema: '', setDatabaseSchema: vi.fn(), logs: [], isDeploying: false, handleFormatDdl: vi.fn(), handleCopyDdl: vi.fn(), handleDownloadDdl: vi.fn(), handleDownloadDoc: vi.fn(), handleDeploySandbox: vi.fn(), handleGenerateTestData: vi.fn() }) }));
vi.mock('@/features/sandbox-deployment/components/DdlCodeEditor', () => ({ DdlCodeEditor: () => null }));
vi.mock('@/features/sandbox-deployment/components/SandboxConfigCard', () => ({ SandboxConfigCard: () => null }));

describe('workflow screen navigation', () => {
  beforeEach(() => { mocks.push.mockReset(); mocks.analyzeProject.mockResolvedValue(PROJECT_ID); });

  it('chuyển Project Init sang Modeling sau phân tích', async () => {
    render(<ProjectInitScreen />);
    fireEvent.click(screen.getByRole('button', { name: 'analyze' }));
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith(`/?step=modeling&project_id=${PROJECT_ID}`));
  });

  it('công bố đúng liên kết của Modeling', () => {
    render(<ModelingDashboardScreen projectId="project-1" />);
    expect(screen.getByRole('link', { name: /BTN_RECONFIGURE/ })).toHaveAttribute('href', '/projects/project-1?step=project-init');
    expect(screen.getByRole('link', { name: /BTN_RUN_SANDBOX/ })).toHaveAttribute('href', '/projects/project-1?step=sandbox');
  });

  it('cho phép Sandbox quay lại Modeling', () => {
    render(<SandboxDeploymentScreen projectId="project-1" />);
    expect(screen.getByRole('link', { name: /BTN_BACK_TO_MODELING/ })).toHaveAttribute('href', '/projects/project-1?step=modeling');
  });
});
