import { describe, expect, it } from 'vitest';
import { parseDbml, serializeDbml } from '@/common/dbml/dbml-adapter';
import { SAMPLE_DBML } from '../../model-document/utils/sample-dbml';
import { createReferenceFromConnection, mapDocumentToGraph } from './erd-graph-mapper';

function fixture() {
  const result = parseDbml(SAMPLE_DBML);
  if (!result.document) throw new Error('TEST_FIXTURE_INVALID');
  return result.document;
}

describe('ERD graph mapper', () => {
  it('đồng bộ DBML -> draft -> graph và serialize ngược lại', () => {
    const document = fixture();
    const graph = mapDocumentToGraph(document, {});
    expect(graph.nodes).toHaveLength(document.tables.length);
    expect(graph.edges).toHaveLength(document.references.length);
    expect(parseDbml(serializeDbml(document)).document?.references).toHaveLength(document.references.length);
  });

  it('tạo relationship many-to-one từ handle cột', () => {
    const document = { ...fixture(), references: [] };
    const sourceTable = document.tables[0];
    const targetTable = document.tables[1];
    const reference = createReferenceFromConnection(document, {
      source: sourceTable.id,
      target: targetTable.id,
      sourceHandle: `source:${sourceTable.id}:${sourceTable.columns[1].id}`,
      targetHandle: `target:${targetTable.id}:${targetTable.columns[0].id}`,
    });
    expect(reference).toMatchObject({ fromTable: sourceTable.name, toTable: targetTable.name, relation: '>' });
  });
});
