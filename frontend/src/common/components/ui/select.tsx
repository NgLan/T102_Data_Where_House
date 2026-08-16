/**
 * Pure Presentation Component: Select dropdown
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement>;

export const Select: React.FC<SelectProps> = ({ children, className, ...props }) => {
  return (
    <select
      className={cn(
        'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white text-slate-900 outline-none transition-colors focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
};
