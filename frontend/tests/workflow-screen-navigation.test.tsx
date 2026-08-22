// @vitest-environment jsdom

import type { ReactNode } from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ModelingDashboardScreen } from "@/features/modeling-dashboard/ModelingDashboardScreen";
import { ProjectInitScreen } from "@/features/project-init";
import { SandboxDeploymentScreen } from "@/features/sandbox-deployment";

const PROJECT_ID = "2f4a682b-78f5-4b3e-8b25-fc9ca3387df0";
const mocks = vi.hoisted(() => ({ push: vi.fn(), saveProject: vi.fn(), analyze: vi.fn() }));

afterEach(cleanup);
vi.mock("react-i18next", () => ({ initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock("next/link", () => ({ default: ({ href, children }: { href: string; children: ReactNode }) => <a href={href}>{children}</a> }));
vi.mock("@/common/components/layout/AppHeader", () => ({ AppHeader: () => <header>app-header</header> }));
vi.mock("@/features/project-init/project-init-screen/project-details/hooks/use-project-details", () => ({ useProjectDetails: () => ({
  form: { formState: { isDirty: false } }, save: mocks.saveProject,
  updateMutation: { isPending: false },
  projectQuery: { data: { requirements: [] }, isLoading: false, isError: false, refetch: vi.fn() },
}) }));
vi.mock("@/features/project-init/project-init-screen/data-sources/hooks/use-data-sources", () => ({ useDataSources: () => ({
  canEdit: true, deleteSource: vi.fn(), isMutating: false, sources: [], uploadCsvFiles: vi.fn(),
  sourcesQuery: { isLoading: false, isError: false, refetch: vi.fn() },
}) }));
vi.mock("@/features/project-init/project-init-screen/hooks/use-project-analysis", () => ({ useProjectAnalysis: () => ({
  analyze: mocks.analyze, analysisMutation: { isPending: false },
  statusQuery: { data: { requirement_analysis_outdated: false, source_analysis_outdated: false } },
}) }));
vi.mock("@/features/project-init/project-init-screen/DataSourceSection", () => ({ DataSourceSection: () => null }));
vi.mock("@/features/project-init/project-init-screen/ProjectDetailsForm", () => ({ ProjectDetailsForm: () => null }));
vi.mock("@/features/project-init/project-init-screen/PiiGuardNotice", () => ({ PiiGuardNotice: () => null }));
vi.mock("@/features/modeling-dashboard/ai-insights/hooks/use-ai-insights", () => ({ useAiInsights: () => ({ isWidgetOpen: false, toggleWidget: vi.fn(), selectedTableFilter: "ALL", setSelectedTableFilter: vi.fn(), insights: [], tableNames: [], totalCount: 0 }) }));
vi.mock("@/features/modeling-dashboard/modeling-workspace/components/ModelingWorkspace", () => ({ ModelingWorkspace: ({ projectId }: { projectId: string }) => <div>
  <a href={`/projects/${projectId}?step=project-init`}>BTN_RECONFIGURE</a>
  <a href={`/projects/${projectId}?step=sandbox`}>BTN_RUN_SANDBOX</a></div> }));
vi.mock("@/features/modeling-dashboard/ai-insights/components/AIInsightsPanel", () => ({ AIInsightsPanel: () => null }));
vi.mock("@/features/sandbox-deployment/sandbox-deployment-screen/ddl-editor/hooks/use-ddl-editor", () => ({
  useDdlEditor: () => ({ ddlCode: "", dialect: "POSTGRESQL" }),
}));
vi.mock("@/features/sandbox-deployment/sandbox-deployment-screen/sandbox-config/hooks/use-sandbox-config", () => ({
  useSandboxConfig: () => ({ form: { watch: () => "sandbox_db" }, savedConfig: null }),
}));
vi.mock("@/features/sandbox-deployment/sandbox-deployment-screen/sandbox-execution/hooks/use-sandbox-execution", () => ({
  useSandboxExecution: () => ({}),
}));
vi.mock("@/features/sandbox-deployment/sandbox-deployment-screen/components/SandboxDeploymentContent", () => ({
  SandboxDeploymentContent: () => null,
}));

describe("workflow screen navigation", () => {
  beforeEach(() => { mocks.push.mockReset(); mocks.analyze.mockReset();
    mocks.analyze.mockResolvedValue(undefined); mocks.saveProject.mockResolvedValue(true); });

  it("Lưu & Phân tích tại chỗ mà không chuyển trang", async () => {
    render(<ProjectInitScreen projectId={PROJECT_ID} />);
    fireEvent.click(screen.getByRole("button", { name: /BTN_SAVE_ANALYZE/ }));
    await waitFor(() => expect(mocks.analyze).toHaveBeenCalled());
    expect(mocks.push).not.toHaveBeenCalled();
  });

  it("chỉ chuyển sang Modeling bằng nút Tiếp tục", () => {
    render(<ProjectInitScreen projectId={PROJECT_ID} />);
    fireEvent.click(screen.getByRole("button", { name: /BTN_CONTINUE/ }));
    expect(mocks.push).toHaveBeenCalledWith(`/projects/${PROJECT_ID}?step=modeling`);
  });

  it("công bố đúng liên kết của Modeling", () => {
    render(<ModelingDashboardScreen projectId="project-1" />);
    expect(screen.getByRole("link", { name: /BTN_RECONFIGURE/ })).toHaveAttribute("href", "/projects/project-1?step=project-init");
    expect(screen.getByRole("link", { name: /BTN_RUN_SANDBOX/ })).toHaveAttribute("href", "/projects/project-1?step=sandbox");
  });

  it("cho phép Sandbox quay lại Modeling", () => {
    render(<SandboxDeploymentScreen projectId="project-1" />);
    expect(screen.getByRole("link", { name: /BTN_BACK_TO_MODELING/ })).toHaveAttribute("href", "/projects/project-1?step=modeling");
  });
});
