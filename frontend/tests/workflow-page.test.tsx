import { describe, expect, it, vi } from 'vitest';
import HomePage from '@/app/page';
import { ModelingDashboardScreen } from '@/features/modeling-dashboard';
import { ProjectInitScreen } from '@/features/project-init/components/ProjectInitScreen';
import { SandboxDeploymentScreen } from '@/features/sandbox-deployment/components/SandboxDeploymentScreen';

vi.mock('@/features/project-init/components/ProjectInitScreen', () => ({ ProjectInitScreen: vi.fn() }));
vi.mock('@/features/modeling-dashboard', () => ({ ModelingDashboardScreen: vi.fn() }));
vi.mock('@/features/sandbox-deployment/components/SandboxDeploymentScreen', () => ({ SandboxDeploymentScreen: vi.fn() }));

describe('workflow page', () => {
  it.each([
    [undefined, ProjectInitScreen],
    ['invalid', ProjectInitScreen],
    ['project-init', ProjectInitScreen],
    ['modeling', ModelingDashboardScreen],
    ['sandbox', SandboxDeploymentScreen],
  ] as const)('render đúng screen với step %s', async (step, expectedComponent) => {
    const element = await HomePage({ searchParams: Promise.resolve({ step }) });
    expect(element.type).toBe(expectedComponent);
  });
});
