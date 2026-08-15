import { ModelingDashboardScreen } from '@/features/modeling-dashboard';
import { ProjectInitScreen } from '@/features/project-init/components/ProjectInitScreen';
import { SandboxDeploymentScreen } from '@/features/sandbox-deployment/components/SandboxDeploymentScreen';
import { parseWorkflowStep } from '@/common/routing/workflow-routing';

interface HomePageProps {
  searchParams: Promise<{ step?: string | string[] }>;
}

/** Điều hướng route gốc tới feature screen được chọn qua query `step`.
 * @param props Search params do Next.js App Router cung cấp.
 * @returns Feature screen tương ứng hoặc Project Init khi query không hợp lệ.
 */
export default async function HomePage({ searchParams }: HomePageProps) {
  const step = parseWorkflowStep((await searchParams).step);
  if (step === 'modeling') return <ModelingDashboardScreen />;
  if (step === 'sandbox') return <SandboxDeploymentScreen />;
  return <ProjectInitScreen />;
}
