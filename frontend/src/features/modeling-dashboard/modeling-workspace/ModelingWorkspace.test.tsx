// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TooltipProvider } from '@/common/components/ui/tooltip';
import { ModelingWorkspace } from './ModelingWorkspace';

const mocks = vi.hoisted(() => ({ load: vi.fn(), save: vi.fn(), status: 'ready', errorCode: null as string | null }));

vi.mock('react-i18next', () => ({
  initReactI18next: { type: '3rdParty', init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock('@/common/notifications', () => ({
  useAppNotification: () => ({ getErrorMessage: (code: string) => code }),
}));
vi.mock('./components/panels/dbml-editor/components/DBMLEditor', () => ({ DBMLEditor: () => null }));
vi.mock('./components/panels/erd-canvas/components/ERDCanvas', () => ({ ERDCanvas: () => null }));
vi.mock('./components/panels/model-inspector/DataModelInspector', () => ({ DataModelInspector: () => <div>INSPECTOR</div> }));
vi.mock('../agent-sessions/hooks/use-agent-sessions', () => ({
  useAgentSessions: () => ({
    sessions: [],
    selectedSessionId: null,
    events: [],
    pendingClarification: null,
    draft: '',
    isSending: false,
    errorCode: null,
    canSend: false,
    selectSession: vi.fn(),
    setDraft: vi.fn(),
    createSession: vi.fn(),
    send: vi.fn(),
    answerClarification: vi.fn(),
  }),
}));
vi.mock('./hooks/use-modeling-workspace', () => ({ useModelingWorkspace: () => ({
  document: { tables: [], references: [] }, code: '', parseError: null,
  validationErrors: {}, selectedTableId: null, selectedReferenceId: null,
  setSelectedTableId: vi.fn(), setSelectedReferenceId: vi.fn(), selectTable: vi.fn(),
  selectReference: vi.fn(), setCode: vi.fn(), mutate: vi.fn(), addReference: vi.fn(),
  addTable: vi.fn(), addColumn: vi.fn(), canSave: false, isDirty: false,
  status: mocks.status, errorCode: mocks.errorCode, load: mocks.load, save: mocks.save,
  generate: vi.fn(), snapshot: null, applySnapshot: vi.fn(),
}) }));

afterEach(cleanup);

describe('ModelingWorkspace', () => {
  beforeEach(() => { mocks.status = 'ready'; mocks.errorCode = null; mocks.load.mockReset(); });

  it('hiển thị skeleton khi tải snapshot lần đầu', () => {
    mocks.status = 'loading';
    renderWorkspace("project-1");
    expect(screen.getByLabelText('TXT_LOADING')).toBeInTheDocument();
  });

  it('hiển thị lỗi thân thiện khi có conflict', () => {
    mocks.status = 'conflict';
    mocks.errorCode = 'DATA_MODEL_REVISION_CONFLICT';
    renderWorkspace("86fd6b4e-1822-42db-a847-4d580abead3e");
    expect(screen.getByRole('alert')).toHaveTextContent('DATA_MODEL_REVISION_CONFLICT');
  });

  it('đóng inspector mặc định và cho phép mở lại', () => {
    renderWorkspace("project-1");
    expect(screen.queryByText('INSPECTOR')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'BTN_SHOW_INSPECTOR' }));
    expect(screen.getByText('INSPECTOR')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'BTN_HIDE_INSPECTOR' }));
    expect(screen.queryByText('INSPECTOR')).not.toBeInTheDocument();
  });

  it('cho phép bật/tắt AI qua nút toggle', () => {
    renderWorkspace("project-1");
    const toggleButton = screen.getByRole('button', { name: 'BTN_HIDE_AGENT' });
    expect(toggleButton).toBeInTheDocument();
    fireEvent.click(toggleButton);
    expect(screen.getByRole('button', { name: 'BTN_SHOW_AGENT' })).toBeInTheDocument();
  });
});

function renderWorkspace(projectId: string) {
  return render(
    <TooltipProvider><ModelingWorkspace projectId={projectId} /></TooltipProvider>,
  );
}
