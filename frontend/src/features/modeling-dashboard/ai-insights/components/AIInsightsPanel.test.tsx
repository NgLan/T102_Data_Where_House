// @vitest-environment jsdom

import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AIInsightsPanel } from './AIInsightsPanel';

vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

describe('AIInsightsPanel', () => {
  it('hiển thị empty state khi bộ lọc không có insight', () => {
    render(<AIInsightsPanel isOpen onToggle={vi.fn()} selectedFilter="ALL" onFilterChange={vi.fn()} insights={[]} tableNames={[]} totalCount={0} isLoading={false} errorMessage={null} onRetry={vi.fn()} />);
    expect(screen.getByText('TXT_EMPTY_INSIGHTS')).toBeInTheDocument();
  });
});
