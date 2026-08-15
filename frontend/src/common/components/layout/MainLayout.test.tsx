// @vitest-environment jsdom

import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { MainLayout } from './MainLayout';

afterEach(cleanup);

describe('MainLayout', () => {
  it('dùng chiều rộng giới hạn theo mặc định', () => {
    render(<MainLayout><span>content</span></MainLayout>);
    expect(screen.getByText('content').parentElement).toHaveClass('max-w-7xl');
  });

  it('cho phép feature dùng toàn chiều rộng', () => {
    render(<MainLayout isFullWidth><span>content</span></MainLayout>);
    expect(screen.getByText('content').parentElement).toHaveClass('max-w-none');
  });

  it('loại bỏ padding và margin cho workspace flush', () => {
    render(<MainLayout isFullWidth isFlush><span>content</span></MainLayout>);
    const content = screen.getByText('content');
    expect(content.closest('main')).toHaveClass('p-0', 'overflow-hidden');
    expect(content.parentElement).not.toHaveClass('mx-auto');
  });
});
