/**
 * Presentation Component: App shell dùng chung có AppHeader.
 */

import type { ReactNode } from 'react';
import { cn } from '@/common/lib/utils';
import { AppHeader } from './AppHeader';

export interface MainLayoutProps {
  children: ReactNode;
  isFullWidth?: boolean;
  isFlush?: boolean;
  selectedProjectId?: string;
}

/** Cung cấp khung hiển thị và vùng cuộn dùng chung cho các feature screen.
 * @param props Nội dung màn hình và lựa chọn chiều rộng.
 * @returns Layout có nền, vùng cuộn và content container responsive.
 */
export function MainLayout({
  children, isFullWidth = false, isFlush = false, selectedProjectId,
}: MainLayoutProps) {
  return (
    <div className="relative flex h-dvh flex-col overflow-hidden bg-background font-sans text-foreground">
      <div className="pointer-events-none absolute left-1/4 top-0 -z-10 size-96 rounded-full bg-red-400/10 blur-3xl" />
      <div className="pointer-events-none absolute right-1/4 top-1/3 -z-10 size-96 rounded-full bg-rose-400/10 blur-3xl" />
      <AppHeader selectedProjectId={selectedProjectId} />
      <main className={cn('flex min-h-0 flex-1 flex-col animate-in fade-in slide-in-from-bottom-2 duration-300', isFlush ? 'overflow-hidden p-0' : 'overflow-y-auto p-2 sm:px-6 sm:py-5')}>
        <div className={cn('flex min-h-0 w-full flex-1 flex-col', !isFlush && 'mx-auto', isFullWidth ? 'max-w-none' : 'max-w-7xl')}>
          {children}
        </div>
      </main>
    </div>
  );
}
