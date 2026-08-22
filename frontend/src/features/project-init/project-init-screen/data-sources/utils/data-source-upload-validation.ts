import type { DataSourceResponse } from "@/api";

const MAX_SOURCES = 20;
const MAX_FILE_SIZE = 20 * 1024 * 1024;

/** Kiểm tra nhanh file CSV và tổng source sau upload; Backend vẫn là nguồn quyết định cuối. */
export function validateCsvFiles(files: File[], sources: DataSourceResponse[]): string | null {
  if (!files.length) return "FILE_EMPTY";
  if (files.some((file) => file.size > MAX_FILE_SIZE)) return "FILE_TOO_LARGE";
  if (files.some((file) => !file.name.toLowerCase().endsWith(".csv"))) {
    return "INVALID_FILE_FORMAT";
  }
  const names = new Set(sources.map((source) => source.name.toLowerCase()));
  files.forEach((file) => names.add(file.name.toLowerCase()));
  return names.size > MAX_SOURCES ? "MAX_FILES_EXCEEDED" : null;
}
