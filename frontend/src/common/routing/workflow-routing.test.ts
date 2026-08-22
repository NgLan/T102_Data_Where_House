import { describe, expect, it } from 'vitest';
import { createWorkflowHref, parseWorkflowStep } from './workflow-routing';

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

  it('đưa project vào đường dẫn, bước workflow vào query', () => {
    // Định danh dự án nằm ở path segment (`src/app/projects/[id]/page.tsx`), không phải
    // query `project_id` như thiết kế cũ.
    expect(createWorkflowHref('sandbox', PROJECT_ID)).toBe(
      `/projects/${PROJECT_ID}?step=sandbox`,
    );
  });

  it('trỏ về trang chủ khi chưa có dự án', () => {
    expect(createWorkflowHref('modeling')).toBe('/?step=modeling');
    expect(createWorkflowHref('modeling', null)).toBe('/?step=modeling');
  });

  it('encode giá trị bước để an toàn khi ghép vào URL', () => {
    expect(createWorkflowHref('project-init', PROJECT_ID)).toContain('step=project-init');
  });
});
