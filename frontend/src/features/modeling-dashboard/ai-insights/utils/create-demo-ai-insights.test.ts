import { describe, expect, it, vi } from 'vitest';
import { createDemoAIInsights } from './create-demo-ai-insights';

describe('createDemoAIInsights', () => {
  it('tạo view model local không phụ thuộc API contract', () => {
    const translate = vi.fn((key: string) => key);
    const insights = createDemoAIInsights(translate as never);

    expect(insights).toHaveLength(4);
    expect(insights[0]).toMatchObject({ tableName: 'Fact_Rides', severity: 'info' });
    expect(insights.every((item) => !('table_name' in item))).toBe(true);
  });
});
