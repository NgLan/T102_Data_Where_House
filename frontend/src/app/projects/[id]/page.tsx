import { parseWorkflowStep } from "@/common/routing/workflow-routing";
import { ModelingDashboardScreen } from "@/features/modeling-dashboard";
import { ProjectInitScreen } from "@/features/project-init";
import { SandboxDeploymentScreen } from "@/features/sandbox-deployment";

interface ProjectWorkspacePageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ step?: string | string[] }>;
}

/** Điều hướng Không gian làm việc dự án (/projects/[id]) tới feature screen tương ứng dựa vào query `step`.
 * @param props Path params và Search params do Next.js App Router cung cấp.
 * @returns Feature screen tương ứng hoặc Project Init khi query không hợp lệ.
 */
export default async function ProjectWorkspacePage({
  params,
  searchParams,
}: ProjectWorkspacePageProps) {
  const { id } = await params;
  const step = parseWorkflowStep((await searchParams).step);
  if (step === "modeling") return <ModelingDashboardScreen projectId={id} />;
  if (step === "sandbox") return <SandboxDeploymentScreen projectId={id} />;
  return <ProjectInitScreen projectId={id} />;
}
