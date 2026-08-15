'use client';

import type { ComponentProps, ReactElement, ReactNode } from 'react';
import { Button } from './button';
import {
  Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle, DialogTrigger,
} from './dialog';

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
    <Dialog open={props.isOpen} onOpenChange={props.onOpenChange}>
      {props.trigger && <DialogTrigger asChild>{props.trigger}</DialogTrigger>}
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{props.title}</DialogTitle>
          <DialogDescription asChild><div>{props.content}</div></DialogDescription>
        </DialogHeader>
        <DialogFooter>{props.actions.map((action) => (
          <DialogAction key={action.id} action={action} />
        ))}</DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DialogAction({ action }: { action: ConfirmationDialogAction }) {
  const button = (
    <Button type="button" variant={action.variant} disabled={action.isDisabled}
      onClick={action.onSelect}>{action.label}</Button>
  );
  return action.shouldClose === false ? button : <DialogClose asChild>{button}</DialogClose>;
}
