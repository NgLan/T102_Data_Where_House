import type { DataSourceResponse } from "@/api";

const MAX_SOURCES = 20;
const MAX_FILE_SIZE = 20 * 1024 * 1024;
const SOURCE_EXTENSIONS = [".csv", ".tsv", ".xls", ".xlsx", ".md", ".markdown", ".sql"];

/** Kiểm tra nhanh file source và tổng source; Backend vẫn là nguồn quyết định cuối. */
export function validateSourceFiles(files: File[], sources: DataSourceResponse[]): string | null {
  if (!files.length) return "FILE_EMPTY";
  if (files.some((file) => file.size > MAX_FILE_SIZE)) return "FILE_TOO_LARGE";
  if (files.some((file) => !SOURCE_EXTENSIONS.some((item) => file.name.toLowerCase().endsWith(item)))) {
    return "INVALID_FILE_FORMAT";
  }
  const names = new Set(sources.map((source) => source.name.toLowerCase()));
  files.forEach((file) => names.add(file.name.toLowerCase()));
  return names.size > MAX_SOURCES ? "MAX_FILES_EXCEEDED" : null;
}
