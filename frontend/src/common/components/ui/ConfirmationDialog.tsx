'use client';

import type { ComponentProps, ReactElement, ReactNode } from 'react';
import { Button } from './button';
import {
  AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from './alert-dialog';

type ButtonVariant = ComponentProps<typeof Button>['variant'];

export interface ConfirmationDialogAction {
  id: string;
  label: ReactNode;
  variant?: ButtonVariant;
  isDisabled?: boolean;
  shouldClose?: boolean;
  onSelect?: () => void;
}

interface ConfirmationDialogProps {
  trigger?: ReactElement;
  title: ReactNode;
  content: ReactNode;
  actions: readonly [ConfirmationDialogAction, ...ConfirmationDialogAction[]];
  isOpen?: boolean;
  onOpenChange?: (isOpen: boolean) => void;
}

/** Hiển thị dialog xác nhận có nội dung và số action tùy theo ngữ cảnh. */
export function ConfirmationDialog(props: ConfirmationDialogProps) {
  return (
    <AlertDialog open={props.isOpen} onOpenChange={props.onOpenChange}>
      {props.trigger && <AlertDialogTrigger asChild>{props.trigger}</AlertDialogTrigger>}
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{props.title}</AlertDialogTitle>
          <AlertDialogDescription asChild><div>{props.content}</div></AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>{props.actions.map((action) => (
          <DialogAction key={action.id} action={action} />
        ))}</AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

function DialogAction({ action }: { action: ConfirmationDialogAction }) {
  if (action.shouldClose !== false) {
    return (
      <AlertDialogAction variant={action.variant} disabled={action.isDisabled}
        onClick={action.onSelect}>{action.label}</AlertDialogAction>
    );
  }
  return (
    <Button type="button" variant={action.variant} disabled={action.isDisabled}
      onClick={action.onSelect}>{action.label}</Button>
  );
}
