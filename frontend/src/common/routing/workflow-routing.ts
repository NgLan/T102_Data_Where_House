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
 * @returns URL root có query `step` đã encode.
 */
export function createWorkflowHref(step: WorkflowStep): string {
  return `/?step=${encodeURIComponent(step)}`;
}
