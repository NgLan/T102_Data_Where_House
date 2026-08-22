import corpus from '../../../../../../../tests/fixtures/dbml-corpus.json';
import { describe, expect, it } from 'vitest';
import { parseDbml, serializeDbml } from './dbml-adapter';

describe('DBML adapter', () => {
  it.each(corpus.valid)('parse và export $name', ({ source }) => {
    const parsed = parseDbml(source);

    expect(parsed.error).toBeNull();
    expect(parsed.document).not.toBeNull();

    const exported = serializeDbml(parsed.document!);
    const reparsed = parseDbml(exported);
    expect(reparsed.error).toBeNull();
    expect(reparsed.document?.tables.map((table) => table.name)).toEqual(
      parsed.document?.tables.map((table) => table.name)
    );
  });

  it.each(corpus.invalid)('từ chối $name', ({ source }) => {
    expect(parseDbml(source)).toEqual({
      document: null,
      error: 'DATA_MODEL_DBML_SYNTAX_INVALID',
    });
  });

  it('giữ increment, check và referential actions khi round trip', () => {
    const source = 'Table parents { id integer [pk] }\n'
      + 'Table children {\n id integer [increment]\n parent_id integer\n'
      + ' score integer [default: 1, check: `score > 0`]\n}\n'
      + 'Ref: children.parent_id > parents.id [delete: cascade, update: restrict]';
    const parsed = parseDbml(source);

    expect(parsed.document?.tables[1].columns[0].isAutoIncrement).toBe(true);
    expect(parsed.document?.tables[1].columns[2].checks).toEqual(['score > 0']);
    expect(parsed.document?.references[0]).toMatchObject({
      onDelete: 'cascade', onUpdate: 'restrict', relation: '>',
    });

    const reparsed = parseDbml(serializeDbml(parsed.document!));
    expect(reparsed.document?.tables[1].columns[2].checks).toEqual(['score > 0']);
    expect(reparsed.document?.references[0].onDelete).toBe('cascade');
  });
});
