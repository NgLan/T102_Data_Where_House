// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConfirmationDialog } from './confirmation-dialog';

afterEach(cleanup);

describe('ConfirmationDialog', () => {
  it('hiển thị header, content và số action theo ngữ cảnh', () => {
    const onConfirm = vi.fn();
    render(<ConfirmationDialog isOpen title="Xác nhận thay đổi" content="Nội dung cảnh báo"
      actions={[
        { id: 'later', label: 'Để sau', shouldClose: false },
        { id: 'cancel', label: 'Hủy' },
        { id: 'confirm', label: 'Đồng ý', onSelect: onConfirm },
      ]} />);

    expect(screen.getByRole('heading')).toHaveTextContent('Xác nhận thay đổi');
    expect(screen.getByText('Nội dung cảnh báo')).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(3);
    fireEvent.click(screen.getByRole('button', { name: 'Đồng ý' }));
    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
