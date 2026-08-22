// @vitest-environment jsdom

import { beforeEach, describe, expect, it } from 'vitest';
import { loadCanvasLayout, reconcileCanvasLayout, saveCanvasLayout } from './canvas-layout-storage';

describe('canvas layout storage', () => {
  beforeEach(() => window.localStorage.clear());

  it('restore theo project và prune node đã xóa', () => {
    const layout = { version: 1 as const, positions: { users: { x: 10, y: 20 }, removed: { x: 30, y: 40 } }, viewport: { x: 1, y: 2, zoom: 0.8 } };
    saveCanvasLayout('project-a', layout);
    const restored = reconcileCanvasLayout(loadCanvasLayout('project-a'), ['users', 'orders']);
    expect(restored.positions).toEqual({ users: { x: 10, y: 20 } });
    expect(reconcileCanvasLayout(restored, ['users']).positions.users).toEqual({ x: 10, y: 20 });
    expect(loadCanvasLayout('project-b')).toBeNull();
  });
});
