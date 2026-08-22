// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConfirmationDialog } from './ConfirmationDialog';

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

  it('chỉ đóng với action có contract đóng', () => {
    const onOpenChange = vi.fn();
    render(<ConfirmationDialog isOpen onOpenChange={onOpenChange} title="Confirm"
      content="Warning" actions={[
        { id: 'keep', label: 'Keep open', shouldClose: false },
        { id: 'close', label: 'Close dialog' },
      ]} />);
    fireEvent.click(screen.getByRole('button', { name: 'Keep open' }));
    expect(onOpenChange).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Close dialog' }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('kích hoạt action xác nhận bằng bàn phím', async () => {
    const onConfirm = vi.fn();
    render(<ConfirmationDialog isOpen title="Confirm" content="Warning"
      actions={[{ id: 'confirm', label: 'Confirm action', onSelect: onConfirm }]} />);
    screen.getByRole('button', { name: 'Confirm action' }).focus();
    await userEvent.keyboard('{Enter}');
    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
