// @vitest-environment jsdom

import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ERDCanvas } from './ERDCanvas';

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

describe('ERDCanvas', () => {
  it('hiển thị empty state khi document chưa có bảng', () => {
    render(<ERDCanvas document={{ preamble: '', tables: [], references: [], sourceModel: null }} projectId="draft" selectedTableId={null} selectedReferenceId={null} onSelectTable={vi.fn()} onSelectReference={vi.fn()} onCreateReference={vi.fn()} />);
    expect(screen.getByText('TXT_EMPTY_MODEL_TITLE')).toBeInTheDocument();
  });
});
