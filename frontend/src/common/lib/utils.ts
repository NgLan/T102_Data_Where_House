/**
 * Hàm tiện ích kết hợp class Tailwind CSS sử dụng clsx và tailwind-merge
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Gộp các Tailwind classname động an toàn, chống xung đột class
 * @param inputs Các classname hoặc biểu thức điều kiện class
 * @returns Chuỗi classname đã tối ưu
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
