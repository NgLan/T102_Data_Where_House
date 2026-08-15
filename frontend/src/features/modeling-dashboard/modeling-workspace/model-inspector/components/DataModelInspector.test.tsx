// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { parseDbml } from '@/common/dbml/dbml-adapter';
import { SAMPLE_DBML } from '../../model-document/utils/sample-dbml';
import {
  DEFAULT_INSPECTOR_WIDTH_PX,
  INSPECTOR_KEYBOARD_STEP_PX,
} from '../hooks/use-resizable-inspector';
import { DataModelInspector } from './DataModelInspector';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

afterEach(cleanup);

function fixture() {
  const parsed = parseDbml(SAMPLE_DBML);
  if (!parsed.document) throw new Error('TEST_FIXTURE_INVALID');
  return parsed.document;
}

describe('DataModelInspector', () => {
  it('hiển thị table đang chọn', () => {
    const document = fixture();
    render(<DataModelInspector document={document} validationErrors={{}} selectedTableId={document.tables[0].id} selectedReferenceId={null} mutate={vi.fn()} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />);
    expect(screen.getByDisplayValue(document.tables[0].name)).toBeInTheDocument();
    expect(screen.getAllByRole('combobox', { name: 'DATA_TYPE_LABEL' })).not.toHaveLength(0);
  });

  it('thay đổi độ rộng inspector bằng separator', () => {
    const document = fixture();
    render(<DataModelInspector document={document} validationErrors={{}} selectedTableId={document.tables[0].id} selectedReferenceId={null} mutate={vi.fn()} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />);
    const separator = screen.getByRole('separator', { name: 'BTN_RESIZE_INSPECTOR' });
    fireEvent.keyDown(separator, { key: 'ArrowLeft' });
    expect(separator).toHaveAttribute('aria-valuenow', String(DEFAULT_INSPECTOR_WIDTH_PX + INSPECTOR_KEYBOARD_STEP_PX));
  });

  it('cho chọn kiểu dữ liệu hoặc nhập kiểu khác', () => {
    const document = fixture();
    const mutate = vi.fn();
    render(<DataModelInspector document={document} validationErrors={{}} selectedTableId={document.tables[0].id} selectedReferenceId={null} mutate={mutate} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />);

    fireEvent.change(screen.getAllByRole('combobox', { name: 'DATA_TYPE_LABEL' })[0], { target: { value: '__custom__' } });
    expect(mutate).toHaveBeenCalledWith(expect.objectContaining({
      type: 'update-column', field: 'dataType', value: '',
    }));
  });

  it('đổi cardinality relationship qua reducer action', () => {
    const document = fixture();
    const mutate = vi.fn();
    render(<DataModelInspector document={document} validationErrors={{}} selectedTableId={null} selectedReferenceId={document.references[0].id} mutate={mutate} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />);
    fireEvent.change(screen.getByLabelText('RELATIONSHIP_KIND_LABEL'), { target: { value: 'one-to-one' } });
    expect(mutate).toHaveBeenCalledWith(expect.objectContaining({
      type: 'update-reference', reference: expect.objectContaining({ relation: '-' }),
    }));
  });

  it('hiển thị validation cạnh field và cập nhật checkbox qua reducer', () => {
    const document = fixture();
    const mutate = vi.fn();
    render(<DataModelInspector document={document} validationErrors={{ 'tables.0.name': 'INVALID_IDENTIFIER' }} selectedTableId={document.tables[0].id} selectedReferenceId={null} mutate={mutate} onAddTable={vi.fn()} onAddColumn={vi.fn()} onClearSelection={vi.fn()} />);

    expect(screen.getByRole('alert')).toHaveTextContent('INVALID_IDENTIFIER');
    fireEvent.click(screen.getAllByRole('button', { name: /BTN_COLUMN_SETTINGS/ })[0]);
    fireEvent.click(screen.getAllByRole('checkbox')[0]);
    expect(mutate).toHaveBeenCalledWith(expect.objectContaining({
      type: 'update-column-settings', patch: { isPrimaryKey: false },
    }));
  });
});
