// @vitest-environment jsdom

import { useReducer } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { parseDbml } from '@/common/dbml/dbml-adapter';
import { mapDocumentToGraph } from '../../erd-canvas/utils/erd-graph-mapper';
import { dataModelEditorReducer } from '../../model-document/reducers/data-model-editor-reducer';
import { validateDataModel } from '../../model-document/utils/data-model-validation';
import { SAMPLE_DBML } from '../../model-document/utils/sample-dbml';
import { DataModelInspector } from './DataModelInspector';

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

afterEach(cleanup);

describe('inspector và canvas synchronization', () => {
  it('cập nhật node canvas khi sửa select, checkbox và tên trong inspector', () => {
    render(<SynchronizationHarness />);
    fireEvent.change(screen.getAllByRole('combobox', { name: 'DATA_TYPE_LABEL' })[0], { target: { value: 'bigint' } });
    expect(screen.getByTestId('canvas-data-type')).toHaveTextContent('bigint');
    expandColumnSettings(0);
    fireEvent.click(screen.getAllByRole('checkbox')[0]);
    expect(screen.getByTestId('canvas-primary-key')).toHaveTextContent('false');
    fireEvent.change(screen.getByLabelText('TABLE_NAME_LABEL'), { target: { value: 'rides_v2' } });
    expect(screen.getByTestId('canvas-table-name')).toHaveTextContent('rides_v2');
  });

  it('dùng input số nguyên và báo lỗi default sai kiểu', () => {
    render(<SynchronizationHarness />);
    expandColumnSettings(1);
    const defaultInput = screen.getByRole('spinbutton', { name: 'DEFAULT_LABEL' });
    expect(defaultInput).toHaveAttribute('step', '1');
    fireEvent.change(defaultInput, { target: { value: '1.5' } });
    expect(screen.getByRole('alert')).toHaveTextContent('INVALID_DEFAULT_FOR_DATA_TYPE');
  });
});

function expandColumnSettings(index: number) {
  fireEvent.click(screen.getAllByRole('button', { name: /BTN_COLUMN_SETTINGS/ })[index]);
}

function SynchronizationHarness() {
  const [document, mutate] = useReducer(dataModelEditorReducer, undefined, createDocumentFixture);
  const table = mapDocumentToGraph(document, {}).nodes[0].data.table;
  return (
    <>
      <output data-testid="canvas-table-name">{table.name}</output>
      <output data-testid="canvas-data-type">{table.columns[0].dataType}</output>
      <output data-testid="canvas-primary-key">{String(table.columns[0].isPrimaryKey)}</output>
      <DataModelInspector document={document} validationErrors={validateDataModel(document)} selectedTableId={document.tables[0].id} selectedReferenceId={null} mutate={mutate} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />
    </>
  );
}

function createDocumentFixture() {
  const parsed = parseDbml(SAMPLE_DBML);
  if (!parsed.document) throw new Error('TEST_FIXTURE_INVALID');
  return parsed.document;
}
