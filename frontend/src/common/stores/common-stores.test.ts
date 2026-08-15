import { beforeEach, describe, expect, it } from 'vitest';
import { useProjectStore } from './use-project-store';

describe('project store', () => {
  beforeEach(() => {
    useProjectStore.setState({ projectId: null, activeTableName: null, isHitlModalOpen: false });
  });

  it('mở và đóng trạng thái chỉnh sửa table', () => {
    useProjectStore.getState().openHitlModal('users');
    expect(useProjectStore.getState()).toMatchObject({ activeTableName: 'users', isHitlModalOpen: true });
    useProjectStore.getState().closeHitlModal();
    expect(useProjectStore.getState()).toMatchObject({ activeTableName: null, isHitlModalOpen: false });
  });
});
