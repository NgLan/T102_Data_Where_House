// @vitest-environment jsdom

import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogTitle } from './alert-dialog';
import { Button } from './button';
import { NativeSelect, NativeSelectOption } from './native-select';

describe('shadcn UI primitives', () => {
  it('áp dụng variant destructive cho Button', () => {
    render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('data-variant', 'destructive');
  });

  it('phát change từ NativeSelect', () => {
    const onChange = vi.fn();
    render(
      <NativeSelect aria-label="type" onChange={onChange}>
        <NativeSelectOption value="int">int</NativeSelectOption>
        <NativeSelectOption value="uuid">uuid</NativeSelectOption>
      </NativeSelect>
    );
    fireEvent.change(screen.getByLabelText('type'), { target: { value: 'uuid' } });
    expect(onChange).toHaveBeenCalledOnce();
  });

  it('kích hoạt action của AlertDialog bằng bàn phím', async () => {
    const onConfirm = vi.fn();
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogTitle>Confirm</AlertDialogTitle>
          <AlertDialogAction onClick={onConfirm}>Continue</AlertDialogAction>
        </AlertDialogContent>
      </AlertDialog>
    );
    screen.getByRole('button', { name: 'Continue' }).focus();
    await userEvent.keyboard('{Enter}');
    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
