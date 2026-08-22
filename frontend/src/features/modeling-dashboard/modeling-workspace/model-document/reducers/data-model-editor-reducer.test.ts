import { describe, expect, it } from 'vitest';
import { parseDbml } from '@/features/modeling-dashboard/modeling-workspace/model-document/dbml/dbml-adapter';
import type { DbmlColumn, DbmlReference } from '@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types';
import { SAMPLE_DBML } from '../utils/sample-dbml';
import { dataModelEditorReducer } from './data-model-editor-reducer';

function documentFixture() {
  const parsed = parseDbml(SAMPLE_DBML);
  if (!parsed.document) throw new Error('TEST_FIXTURE_INVALID');
  return parsed.document;
}

const column: DbmlColumn = {
  id: 'new-column', name: 'status', dataType: 'varchar(20)', isPrimaryKey: false,
  isNotNull: false, isUnique: false, isAutoIncrement: false,
  defaultValue: '', note: '', checks: [], extraSettings: [],
};

describe('dataModelEditorReducer', () => {
  it('thêm, sửa và xóa table', () => {
    const original = documentFixture();
    const table = { ...original.tables[0], id: 'new-table', name: 'payments' };
    const added = dataModelEditorReducer(original, { type: 'add-table', table });
    const renamed = dataModelEditorReducer(added, { type: 'update-table', tableId: table.id, field: 'name', value: 'transactions' });
    const removed = dataModelEditorReducer(renamed, { type: 'remove-table', tableId: table.id });
    expect(renamed.tables.at(-1)?.name).toBe('transactions');
    expect(removed.tables).toHaveLength(original.tables.length);
  });

  it('thêm, sửa, xóa column và dọn relationship phụ thuộc', () => {
    const original = documentFixture();
    const table = original.tables[0];
    const added = dataModelEditorReducer(original, { type: 'add-column', tableId: table.id, column });
    const renamed = dataModelEditorReducer(added, { type: 'update-column', tableId: table.id, columnId: column.id, field: 'name', value: 'ride_status' });
    const removed = dataModelEditorReducer(renamed, { type: 'remove-column', tableId: table.id, columnId: table.columns[1].id });
    expect(renamed.tables[0].columns.at(-1)?.name).toBe('ride_status');
    expect(removed.references.some((reference) => reference.fromColumn === table.columns[1].name)).toBe(false);
  });

  it('thêm, đổi cardinality và xóa relationship', () => {
    const original = documentFixture();
    const reference: DbmlReference = { ...original.references[0], id: 'new-reference' };
    const added = dataModelEditorReducer(original, { type: 'add-reference', reference });
    const updated = dataModelEditorReducer(added, { type: 'update-reference', reference: { ...reference, relation: '-' } });
    const removed = dataModelEditorReducer(updated, { type: 'remove-reference', referenceId: reference.id });
    expect(updated.references.find((item) => item.id === reference.id)?.relation).toBe('-');
    expect(removed.references).toHaveLength(original.references.length);
  });

  it('giữ constraint hiệu lực khi tắt PK đơn bằng atomic settings', () => {
    const original = documentFixture();
    const table = original.tables[0];
    const primaryKey = table.columns[0];
    const updated = dataModelEditorReducer(original, {
      type: 'update-column-settings', tableId: table.id,
      columnId: primaryKey.id, patch: { isPrimaryKey: false },
    });

    expect(updated.tables[0].columns[0]).toMatchObject({
      isPrimaryKey: false, isNotNull: true, isUnique: true,
    });
  });
});
