// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  DBML_EDITOR_KEYBOARD_STEP_PX,
  DEFAULT_DBML_EDITOR_WIDTH_PX,
  MAX_DBML_EDITOR_WIDTH_PX,
  MIN_DBML_EDITOR_WIDTH_PX,
} from '../hooks/use-resizable-dbml-editor';
import { DBMLEditor } from './DBMLEditor';

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
afterEach(cleanup);

describe('DBMLEditor', () => {
  it('thay đổi độ rộng bằng separator và giữ trong min/max', () => {
    render(<DBMLEditor code="Table users {}" parseError={null} onChange={vi.fn()} />);
    const separator = screen.getByRole('separator', { name: 'BTN_RESIZE_DBML_EDITOR' });
    fireEvent.keyDown(separator, { key: 'ArrowRight' });
    expect(separator).toHaveAttribute('aria-valuenow', String(DEFAULT_DBML_EDITOR_WIDTH_PX + DBML_EDITOR_KEYBOARD_STEP_PX));

    const eventCount = Math.ceil(MAX_DBML_EDITOR_WIDTH_PX / DBML_EDITOR_KEYBOARD_STEP_PX) + 1;
    for (let index = 0; index < eventCount; index += 1) fireEvent.keyDown(separator, { key: 'ArrowRight' });
    expect(separator).toHaveAttribute('aria-valuenow', String(MAX_DBML_EDITOR_WIDTH_PX));
    for (let index = 0; index < eventCount * 2; index += 1) fireEvent.keyDown(separator, { key: 'ArrowLeft' });
    expect(separator).toHaveAttribute('aria-valuenow', String(MIN_DBML_EDITOR_WIDTH_PX));
  });
});
