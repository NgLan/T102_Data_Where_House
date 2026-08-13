/**
 * Pure Presentation Component: Badge tag
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'fact' | 'dim' | 'info' | 'warn' | 'error';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = 'default',
  ...props
}) => {
  const variantStyles = {
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    fact: 'bg-blue-600 text-white font-bold',
    dim: 'bg-emerald-500 text-white font-bold',
    info: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    warn: 'bg-amber-50 text-amber-800 border-amber-200',
    error: 'bg-red-50 text-red-800 border-red-200',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border border-transparent',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
