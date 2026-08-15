import { ModelExporter, Parser, type RawDatabase } from '@dbml/core';
import { fromDatabaseModel, toDatabaseModel } from './dbml-mapper';
import type { DbmlDocument, DbmlParseResult } from './types';

/**
 * Chuyển DBML thành view model của editor bằng parser chính thức.
 *
 * @param source Nội dung DBML cần đọc.
 * @returns Kết quả parse với document hoặc mã lỗi chuẩn của UI.
 */
export function parseDbml(source: string): DbmlParseResult {
  try {
    Parser.parse(source, 'dbmlv2');
    return { document: fromDatabaseModel(Parser.parseDBMLToJSONv2(source)), error: null };
  } catch {
    return { document: null, error: 'INVALID_DBML_CONTENT' };
  }
}

/**
 * Xuất view model thành DBML thông qua model và exporter chính thức.
 *
 * @param document View model hiện tại của editor.
 * @returns DBML đã được chuẩn hóa bởi `@dbml/core`.
 * @throws Lỗi compiler của `@dbml/core` nếu model không hợp lệ.
 */
export function serializeDbml(document: DbmlDocument): string {
  const database = Parser.parse(toDatabaseModel(document) as unknown as RawDatabase, 'json');
  return ModelExporter.export(database, 'dbml');
}
