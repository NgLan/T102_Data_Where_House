import { describe, expect, it } from 'vitest';
import type { ERDTableNode } from '../types/erd-canvas-types';
import { calculateErdLayout } from './erd-layout';

describe('ELK layout', () => {
  it('bố trí 20 bảng không trùng tọa độ', async () => {
    const nodes = Array.from({ length: 20 }, (_, index): ERDTableNode => ({
      id: `table-${index}`,
      type: 'erd-table',
      position: { x: 0, y: 0 },
      data: { table: { id: `table-${index}`, schemaName: 'public', name: `table_${index}`, note: '', columns: [], extraStatements: [] } },
    }));
    const positions = await calculateErdLayout(nodes, []);
    expect(Object.keys(positions)).toHaveLength(20);
    const boxes = Object.values(positions).map(({ x, y }) => ({ x, y, right: x + 260, bottom: y + 76 }));
    boxes.forEach((box, index) => boxes.slice(index + 1).forEach((other) => {
      const overlaps = box.x < other.right && box.right > other.x
        && box.y < other.bottom && box.bottom > other.y;
      expect(overlaps).toBe(false);
    }));
  });
});
