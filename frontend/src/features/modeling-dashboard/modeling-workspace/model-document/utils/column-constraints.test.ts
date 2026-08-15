import { describe, expect, it } from 'vitest';
import { parseDbml } from '@/common/dbml/dbml-adapter';
import { getDataTypeChangeImpact, getEffectiveColumnConstraints } from './column-constraints';

function parseFixture(source: string) {
  const parsed = parseDbml(source);
  if (!parsed.document) throw new Error('TEST_FIXTURE_INVALID');
  return parsed.document;
}

describe('column constraints', () => {
  it('PK đơn có hiệu lực not null và unique', () => {
    const document = parseFixture('Table users { id integer [pk] }');
    const [table] = document.tables;

    expect(getEffectiveColumnConstraints(table, table.columns[0])).toEqual({
      isNotNull: true, isUnique: true, isCompositePrimaryKey: false,
    });
  });

  it('không coi từng cột trong composite PK là unique độc lập', () => {
    const document = parseFixture(
      'Table memberships { user_id integer [pk]\n group_id integer [pk] }',
    );
    const [table] = document.tables;

    expect(getEffectiveColumnConstraints(table, table.columns[0]).isUnique).toBe(false);
  });

  it('liệt kê default, increment và FK phải dọn khi đổi type', () => {
    const document = parseFixture(
      'Table parents { id integer [pk] }\n'
      + 'Table children { parent_id integer [increment, default: 1] }\n'
      + 'Ref: children.parent_id > parents.id',
    );
    const table = document.tables[1];
    const impact = getDataTypeChangeImpact({ document, table,
      column: table.columns[0], nextDataType: 'boolean' });

    expect(impact).toEqual({
      shouldClearDefault: true,
      shouldDisableIncrement: true,
      referenceIds: [document.references[0].id],
    });
  });
});
