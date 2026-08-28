import { ModelExporter, Parser, type RawDatabase } from '@dbml/core';
import {
  mapDbmlLibraryModelToDocument,
  mapDocumentToDbmlLibraryModel,
} from './dbml-mapper';
import type { DbmlDocument, DbmlParseResult } from './types';

/**
 * Chuyển DBML thành view model của editor bằng parser chính thức.
 *
 * @param source Nội dung DBML cần đọc.
 * @returns Kết quả parse với document hoặc mã lỗi chuẩn của UI và vị trí lỗi cú pháp.
 */
export function parseDbml(source: string): DbmlParseResult {
  try {
    Parser.parse(source, 'dbmlv2');
    return {
      document: mapDbmlLibraryModelToDocument(Parser.parseDBMLToJSONv2(source)),
      error: null,
      syntaxErrors: [],
    };
  } catch (err: unknown) {
    return {
      document: null,
      error: 'DATA_MODEL_DBML_SYNTAX_INVALID',
      syntaxErrors: extractSyntaxErrors(err),
    };
  }
}

/** Trích xuất danh sách vị trí lỗi từ CompilerDiagnostic của @dbml/core. */
function extractSyntaxErrors(err: unknown): DbmlParseResult['syntaxErrors'] {
  if (!err || typeof err !== 'object' || !('diags' in err)) return [];
  const diags = (err as { diags: unknown }).diags;
  if (!Array.isArray(diags)) return [];

  return diags.flatMap((diag: { location?: { start?: { line?: number; column?: number }; end?: { line?: number; column?: number } }; message?: string }) => {
    if (!diag.location?.start?.line) return [];
    return [{
      line: diag.location.start.line,
      column: diag.location.start.column ?? 1,
      endLine: diag.location.end?.line ?? diag.location.start.line,
      endColumn: diag.location.end?.column ?? (diag.location.start.column ?? 1) + 1,
      message: diag.message ?? 'DATA_MODEL_DBML_SYNTAX_INVALID',
    }];
  });
}

/**
 * Xuất view model thành DBML thông qua model và exporter chính thức.
 *
 * @param document View model hiện tại của editor.
 * @returns DBML đã được chuẩn hóa bởi `@dbml/core`.
 * @throws Lỗi compiler của `@dbml/core` nếu model không hợp lệ.
 */
export function serializeDbml(document: DbmlDocument): string {
  const database = Parser.parse(
    mapDocumentToDbmlLibraryModel(document) as unknown as RawDatabase,
    'json',
  );
  return ModelExporter.export(database, 'dbml');
}
