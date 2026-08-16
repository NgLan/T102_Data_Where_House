/**
 * Presentation Component: Main Layout không có AppHeader
 */

import type { ReactNode } from 'react';
import { cn } from '@/common/lib/utils';

export interface MainLayoutProps {
  children: ReactNode;
  isFullWidth?: boolean;
  isFlush?: boolean;
}

/** Cung cấp khung hiển thị và vùng cuộn dùng chung cho các feature screen.
 * @param props Nội dung màn hình và lựa chọn chiều rộng.
 * @returns Layout có nền, vùng cuộn và content container responsive.
 */
export function MainLayout({ children, isFullWidth = false, isFlush = false }: MainLayoutProps) {
  return (
    <div className="relative flex h-dvh flex-col overflow-hidden bg-slate-50/90 font-sans text-slate-900">
      <div className="pointer-events-none absolute left-1/4 top-0 -z-10 size-96 rounded-full bg-blue-400/10 blur-3xl" />
      <div className="pointer-events-none absolute right-1/4 top-1/3 -z-10 size-96 rounded-full bg-indigo-400/10 blur-3xl" />
      <main className={cn('flex min-h-0 flex-1 flex-col animate-in fade-in slide-in-from-bottom-2 duration-300', isFlush ? 'overflow-hidden p-0' : 'overflow-y-auto p-2 sm:px-6 sm:py-5')}>
        <div className={cn('flex min-h-0 w-full flex-1 flex-col', !isFlush && 'mx-auto', isFullWidth ? 'max-w-none' : 'max-w-7xl')}>
          {children}
        </div>
      </main>
    </div>
  );
}
