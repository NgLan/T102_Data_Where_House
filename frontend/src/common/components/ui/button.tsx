/**
 * Presentation Component: Button UI với các variants (primary, secondary, outline, danger)
 */

import React from 'react';
import { cn } from '@/common/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-bold transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.98]';

  const variantStyles = {
    primary: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-sm shadow-blue-500/20 hover:shadow-md hover:-translate-y-0.5',
    secondary: 'bg-slate-100 hover:bg-slate-200/80 text-slate-800 border border-slate-200/80',
    outline: 'bg-transparent border border-blue-600/80 text-blue-600 hover:bg-blue-50/80',
    danger: 'bg-rose-50 hover:bg-rose-100/80 text-rose-600 border border-rose-200/80',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs rounded-xl',
    md: 'px-4 py-2 text-xs rounded-xl',
    lg: 'px-5 py-2.5 text-sm rounded-xl',
  };

  return (
    <button
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      {...props}
    >
      {children}
    </button>
  );
};

