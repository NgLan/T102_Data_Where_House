// @vitest-environment jsdom

import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ModelingDashboardScreen } from "@/features/modeling-dashboard/ModelingDashboardScreen";
import { ProjectInitScreen } from "@/features/project-init";
import { SandboxDeploymentScreen } from "@/features/sandbox-deployment";

const PROJECT_ID = "2f4a682b-78f5-4b3e-8b25-fc9ca3387df0";
const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  runWorkflow: vi.fn(),
  saveDraft: vi.fn(),
}));

afterEach(cleanup);
vi.mock("react-i18next", () => ({ initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mocks.push }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("next/link", () => ({ default: ({ href, children }: { href: string; children: ReactNode }) => <a href={href}>{children}</a> }));
vi.mock("@/common/components/layout/ProjectSwitcher", () => ({ ProjectSwitcher: () => <div data-testid="project-switcher" /> }));
vi.mock("@/common/components/layout/LanguageSwitcher", () => ({ LanguageSwitcher: () => null }));
vi.mock("@/common/components/layout/ThemeSwitcher", () => ({ ThemeSwitcher: () => null }));
vi.mock("@/common/components/layout/UserMenu", () => ({ UserMenu: () => null }));
vi.mock("@/features/project-init/project-init-screen/project-details/hooks/use-project-details", () => ({ useProjectDetails: () => ({
  form: { formState: { isDirty: false } }, saveDraft: mocks.saveDraft,
  saveInputsForWorkflow: mocks.saveDraft,
  isInfoDirty: false, isRequirementDirty: false,
  updateMutation: { isPending: false },
  rawRequirementMutation: { isPending: false },
  projectQuery: { data: { requirements: [], requirement_revision: 1 }, isLoading: false, isError: false, refetch: vi.fn() },
}) }));
vi.mock("@/features/project-init/project-init-screen/data-sources/hooks/use-data-sources", () => ({ useDataSources: () => ({
  canEdit: true, deleteSource: vi.fn(), isMutating: false, sources: [], uploadCsvFiles: vi.fn(),
  sourcesQuery: { isLoading: false, isError: false, refetch: vi.fn() },
}) }));
vi.mock("@/features/project-init/project-init-screen/hooks/use-project-analysis", () => ({ useProjectAnalysis: () => ({
  statusQuery: { data: { requirement_analysis_outdated: false, source_analysis_outdated: false, data_model_exists: true } },
  initializationMutation: { isPending: false },
}) }));
vi.mock("@/features/project-init/project-init-screen/requirement-workspace/hooks/use-requirement-clarification", () => ({
  useRequirementClarification: () => ({ isProcessing: false }),
}));
vi.mock("@/features/project-init/project-init-screen/hooks/use-project-init-workflow", () => ({
  useProjectInitWorkflow: () => ({
    phase: "IDLE", isRunning: false, sourceGaps: [], isSourceGapStale: false,
    run: mocks.runWorkflow, continueAnalysis: vi.fn(), markSourceGapStale: vi.fn(),
  }),
}));
vi.mock("@/features/project-init/project-init-screen/DataSourceSection", () => ({ DataSourceSection: () => null }));
vi.mock("@/features/project-init/project-init-screen/ProjectDetailsForm", () => ({ ProjectDetailsForm: () => null }));
vi.mock("@/features/project-init/project-init-screen/requirement-workspace/components/RequirementWorkspace", () => ({
  RequirementWorkspace: () => null,
}));
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
  beforeEach(() => {
    mocks.push.mockReset();
    mocks.saveDraft.mockReset().mockResolvedValue(true);
    mocks.runWorkflow.mockReset().mockResolvedValue(undefined);
  });

  it("không tự chuyển trang trước khi người dùng chạy workflow", () => {
    renderWithQuery(<ProjectInitScreen projectId={PROJECT_ID} />);
    expect(mocks.push).not.toHaveBeenCalled();
  });

  it("dùng Lưu và phân tích làm entry point workflow duy nhất", async () => {
    renderWithQuery(<ProjectInitScreen projectId={PROJECT_ID} />);
    fireEvent.click(screen.getByRole("button", { name: /BTN_SAVE_AND_ANALYZE/ }));
    await waitFor(() => expect(mocks.runWorkflow).toHaveBeenCalledOnce());
  });

  it("giữ Project Init khi workflow pause để clarification", async () => {
    renderWithQuery(<ProjectInitScreen projectId={PROJECT_ID} />);
    fireEvent.click(screen.getByRole("button", { name: /BTN_SAVE_AND_ANALYZE/ }));
    await waitFor(() => expect(mocks.runWorkflow).toHaveBeenCalledOnce());
    expect(mocks.push).not.toHaveBeenCalled();
  });

  it("công bố đúng liên kết của Modeling", () => {
    renderWithQuery(<ModelingDashboardScreen projectId="project-1" />);
    expect(screen.getAllByRole("link", { name: /TXT_WORKFLOW_STEP_PROJECT_INIT/ })[0]).toHaveAttribute("href", "/projects/project-1?step=project-init");
    expect(screen.getAllByRole("link", { name: /TXT_WORKFLOW_STEP_SANDBOX/ })[0]).toHaveAttribute("href", "/projects/project-1?step=sandbox");
  });

  it("cho phép Sandbox quay lại Modeling", () => {
    renderWithQuery(<SandboxDeploymentScreen projectId="project-1" />);
    expect(screen.getAllByRole("link", { name: /TXT_WORKFLOW_STEP_MODELING/ })[0]).toHaveAttribute("href", "/projects/project-1?step=modeling");
  });
});

function renderWithQuery(node: ReactNode) {
  const client = new QueryClient();
  client.setQueryData(["project-init", "status", "project-1"], {
    data_model_exists: true,
  });
  return render(<QueryClientProvider client={client}>{node}</QueryClientProvider>);
}
