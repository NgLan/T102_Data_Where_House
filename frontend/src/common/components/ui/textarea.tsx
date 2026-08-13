/**
 * Pure Presentation Component: Textarea field
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea: React.FC<TextareaProps> = ({ className, ...props }) => {
  return (
    <textarea
      className={cn(
        'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white text-slate-900 outline-none transition-colors focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 resize-y',
        className
      )}
      {...props}
    />
  );
};
