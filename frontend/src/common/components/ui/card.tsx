/**
 * Pure Presentation Component: Card container bọc nội dung
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export type CardProps = React.HTMLAttributes<HTMLDivElement>;

export const Card: React.FC<CardProps> = ({ children, className, ...props }) => {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-5',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
