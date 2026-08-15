import { describe, expect, it } from 'vitest';
import { createWorkflowHref, parseWorkflowStep } from './workflow-routing';

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
  });
});
