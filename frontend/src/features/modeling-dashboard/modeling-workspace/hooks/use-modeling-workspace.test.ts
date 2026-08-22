// @vitest-environment jsdom

import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { getDataModel, updateDataModel } from '@/api';
import { SAMPLE_DBML } from '../model-document/utils/sample-dbml';
import { useModelingWorkspace } from './use-modeling-workspace';

vi.mock('@/api', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/api')>()),
  apiClient: {},
  getDataModel: vi.fn(),
  updateDataModel: vi.fn(),
}));

const snapshot = {
  id: 'model-1', project_id: 'project-1', dbml: SAMPLE_DBML, revision: 3,
  created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
};

describe('useModelingWorkspace', () => {
  beforeEach(() => {
    vi.mocked(getDataModel).mockResolvedValue({ data: { data: snapshot } } as never);
    vi.mocked(updateDataModel).mockReset();
  });

  it('giữ draft và báo conflict khi server có revision mới hơn', async () => {
    vi.mocked(updateDataModel).mockRejectedValue({
      code: 409, message: 'Conflict', error_code: 'DATA_MODEL_REVISION_CONFLICT',
    });
    const { result } = renderHook(() => useModelingWorkspace('project-1'));
    await waitFor(() => expect(result.current.status).toBe('ready'));
    act(() => result.current.setCode(`${SAMPLE_DBML}\n// local change`));
    await waitFor(() => expect(result.current.isDirty).toBe(true));
    await act(async () => result.current.save());
    expect(result.current.status).toBe('conflict');
    expect(result.current.errorCode).toBe('DATA_MODEL_REVISION_CONFLICT');
    expect(result.current.canSave).toBe(false);
    expect(result.current.code).toContain('// local change');
  });

  it('gọi generated SDK với client, project path và base revision', async () => {
    vi.mocked(updateDataModel).mockResolvedValue({
      data: { data: { ...snapshot, revision: 4 } },
    } as never);
    const { result } = renderHook(() => useModelingWorkspace('project-1'));
    await waitFor(() => expect(result.current.status).toBe('ready'));

    act(() => result.current.mutate({
      type: 'update-table', tableId: result.current.document.tables[0].id,
      field: 'note', value: 'updated',
    }));
    await act(async () => result.current.save());

    expect(getDataModel).toHaveBeenCalledWith(expect.objectContaining({
      client: expect.anything(), path: { project_id: 'project-1' },
      responseStyle: 'fields', throwOnError: true,
    }));
    expect(updateDataModel).toHaveBeenCalledWith(expect.objectContaining({
      body: expect.objectContaining({ data_model_id: 'model-1', base_revision: 3 }),
      path: { project_id: 'project-1' }, responseStyle: 'fields', throwOnError: true,
    }));
    expect(result.current.snapshot?.revision).toBe(4);
    expect(result.current.isDirty).toBe(false);
  });

  it('báo lỗi khi success envelope thiếu payload', async () => {
    vi.mocked(getDataModel).mockResolvedValueOnce({ data: { data: null } } as never);
    const { result } = renderHook(() => useModelingWorkspace('project-1'));

    await waitFor(() => expect(result.current.status).toBe('error'));
    expect(result.current.errorCode).toBe('INVALID_API_RESPONSE');
  });

  it('coi Data Model chưa tồn tại là trạng thái empty hợp lệ', async () => {
    vi.mocked(getDataModel).mockRejectedValueOnce({
      code: 404, message: 'Not found', error_code: 'DATA_MODEL_NOT_FOUND', details: [],
    });
    const { result } = renderHook(() => useModelingWorkspace('project-1'));

    await waitFor(() => expect(result.current.status).toBe('empty'));
    expect(result.current.errorCode).toBeNull();
  });

  it('cho phép chỉnh trạng thái trung gian chưa hợp lệ trong inspector', async () => {
    const { result } = renderHook(() => useModelingWorkspace('project-1'));
    await waitFor(() => expect(result.current.status).toBe('ready'));
    const tableId = result.current.document.tables[0].id;
    act(() => result.current.mutate({ type: 'update-table', tableId, field: 'name', value: '' }));
    expect(result.current.document.tables[0].name).toBe('');
    expect(result.current.parseError).toBe('DATA_MODEL_DBML_SYNTAX_INVALID');

    act(() => result.current.mutate({ type: 'update-table', tableId, field: 'name', value: 'rides_v2' }));
    expect(result.current.document.tables[0].name).toBe('rides_v2');
    expect(result.current.parseError).toBeNull();
  });
});
