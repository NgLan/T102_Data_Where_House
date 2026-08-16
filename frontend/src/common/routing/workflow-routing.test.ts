import { describe, expect, it } from 'vitest';
import { createWorkflowHref, parseProjectId, parseWorkflowStep } from './workflow-routing';

const PROJECT_ID = '86fd6b4e-1822-42db-a847-4d580abead3e';

describe('workflow routing', () => {
  it.each([
    ['project-init', 'project-init'],
    ['modeling', 'modeling'],
    ['sandbox', 'sandbox'],
    [undefined, 'project-init'],
    ['invalid', 'project-init'],
    [['sandbox', 'modeling'], 'sandbox'],
  ] as const)('chuẩn hóa %o thành %s', (value, expected) => {
    expect(parseWorkflowStep(value)).toBe(expected);
  });

  it('tạo URL query chuẩn', () => {
    expect(createWorkflowHref('modeling')).toBe('/?step=modeling');
    expect(createWorkflowHref('sandbox', PROJECT_ID)).toBe(
      `/?step=sandbox&project_id=${PROJECT_ID}`,
    );
  });

  it('chỉ nhận project UUID hợp lệ', () => {
    expect(parseProjectId(PROJECT_ID)).toBe(PROJECT_ID);
    expect(parseProjectId('demo-project')).toBeNull();
    expect(parseProjectId(undefined)).toBeNull();
  });
});
