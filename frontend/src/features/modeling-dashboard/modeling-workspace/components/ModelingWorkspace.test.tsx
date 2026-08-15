// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ModelingWorkspace } from './ModelingWorkspace';

const mocks = vi.hoisted(() => ({ load: vi.fn(), save: vi.fn(), status: 'ready', errorCode: null as string | null }));

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock('@/common/stores/use-project-store', () => ({ useProjectStore: (selector: (state: { projectId: string }) => string) => selector({ projectId: 'project-1' }) }));
vi.mock('@/common/hooks/use-app-notification', () => ({
  useAppNotification: () => ({ getErrorMessage: (code: string) => code }),
}));
vi.mock('../dbml-editor/components/DBMLEditor', () => ({ DBMLEditor: () => null }));
vi.mock('../erd-canvas/components/ERDCanvas', () => ({ ERDCanvas: () => null }));
vi.mock('../model-inspector/components/DataModelInspector', () => ({ DataModelInspector: () => <div>INSPECTOR</div> }));
vi.mock('../hooks/use-modeling-workspace', () => ({ useModelingWorkspace: () => ({
  document: { tables: [], references: [] }, code: '', parseError: null,
  validationErrors: {}, selectedTableId: null, selectedReferenceId: null,
  setSelectedTableId: vi.fn(), setSelectedReferenceId: vi.fn(), selectTable: vi.fn(),
  selectReference: vi.fn(), setCode: vi.fn(), mutate: vi.fn(), addReference: vi.fn(),
  addTable: vi.fn(), addColumn: vi.fn(), canSave: false, isDirty: false,
  status: mocks.status, errorCode: mocks.errorCode, load: mocks.load, save: mocks.save,
}) }));

afterEach(cleanup);

describe('ModelingWorkspace', () => {
  beforeEach(() => { mocks.status = 'ready'; mocks.errorCode = null; mocks.load.mockReset(); });

  it('hiển thị skeleton khi tải snapshot lần đầu', () => {
    mocks.status = 'loading';
    render(<ModelingWorkspace />);
    expect(screen.getByLabelText('TXT_LOADING')).toBeInTheDocument();
  });

  it('hiển thị lỗi thân thiện và cho phép thử tải lại', () => {
    mocks.status = 'conflict';
    mocks.errorCode = 'REVISION_CONFLICT';
    render(<ModelingWorkspace />);
    expect(screen.getByRole('alert')).toHaveTextContent('REVISION_CONFLICT');
    fireEvent.click(screen.getByRole('button', { name: /BTN_RELOAD_LATEST/ }));
    expect(mocks.load).toHaveBeenCalledOnce();
  });

  it('cho phép đóng và mở lại inspector', () => {
    render(<ModelingWorkspace />);
    expect(screen.getByText('INSPECTOR')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'BTN_HIDE_INSPECTOR' }));
    expect(screen.queryByText('INSPECTOR')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'BTN_SHOW_INSPECTOR' }));
    expect(screen.getByText('INSPECTOR')).toBeInTheDocument();
  });
});
