/**
 * Pure Presentation Component: Base Dialog Modal Overlay
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const Dialog: React.FC<DialogProps> = ({
  isOpen,
  onClose,
  title,
  children,
  className,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className={cn(
          'w-[920px] max-w-[95vw] h-[640px] max-h-[90vh] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-slate-200',
          className
        )}
      >
        {title && (
          <div className="bg-slate-50 px-6 py-4 flex items-center justify-between border-b border-slate-200">
            <div className="text-base font-bold text-slate-800 flex items-center gap-2">
              {title}
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 text-xl font-semibold w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-200 transition-colors"
            >
              ×
            </button>
          </div>
        )}
        <div className="flex-1 flex overflow-hidden">{children}</div>
      </div>
    </div>
  );
};
