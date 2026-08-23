export const WORKFLOW_STEPS = ['project-init', 'modeling', 'sandbox'] as const;

export type WorkflowStep = typeof WORKFLOW_STEPS[number];

/** Chuẩn hóa giá trị query thành bước workflow hợp lệ.
 * @param value Giá trị `step` lấy từ App Router search params.
 * @returns Bước hợp lệ; mặc định là `project-init` khi thiếu hoặc sai.
 */
export function parseWorkflowStep(value: string | readonly string[] | undefined): WorkflowStep {
  const candidate = Array.isArray(value) ? value[0] : value;
  return WORKFLOW_STEPS.find((step) => step === candidate) ?? 'project-init';
}

/** Tạo URL điều hướng chuẩn cho một bước workflow.
 * @param step Bước đích hợp lệ.
 * @param projectId (Tùy chọn) ID dự án nếu đang ở trong không gian làm việc dự án.
 * @returns URL có query `step` đã encode.
 */
export function createWorkflowHref(step: WorkflowStep, projectId?: string | null): string {
  if (projectId) {
    return `/projects/${projectId}?step=${encodeURIComponent(step)}`;
  }
  return `/?step=${encodeURIComponent(step)}`;
}

/** Chỉ chấp nhận UUID project hợp lệ từ URL. */
export function parseProjectId(value: string | readonly string[] | undefined): string | null {
  const candidate = Array.isArray(value) ? value[0] : value;
  if (!candidate) return null;
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(candidate)
    ? candidate
    : null;
}
