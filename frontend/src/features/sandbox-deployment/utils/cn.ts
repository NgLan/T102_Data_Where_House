import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Gộp class Tailwind có điều kiện và loại bỏ các class xung đột. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
