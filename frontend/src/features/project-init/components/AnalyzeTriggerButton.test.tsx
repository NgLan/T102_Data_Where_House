// @vitest-environment jsdom

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AnalyzeTriggerButton } from './AnalyzeTriggerButton';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

describe('AnalyzeTriggerButton', () => {
  it('vô hiệu hóa thao tác trong lúc phân tích', () => {
    render(<AnalyzeTriggerButton isAnalyzing onAnalyze={vi.fn()} />);

    expect(screen.getByRole('button', { name: 'MSG_ANALYZING' })).toBeDisabled();
  });

  it('gọi callback khi sẵn sàng phân tích', () => {
    const onAnalyze = vi.fn();
    render(<AnalyzeTriggerButton isAnalyzing={false} onAnalyze={onAnalyze} />);

    fireEvent.click(screen.getByRole('button', { name: 'BTN_ANALYZE' }));

    expect(onAnalyze).toHaveBeenCalledOnce();
  });
});
