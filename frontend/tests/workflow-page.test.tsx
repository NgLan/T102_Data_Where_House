import { describe, expect, it, vi } from "vitest";
import HomePage from "@/app/page";
import { MainLayout } from "@/common/components/layout/MainLayout";
import { ProjectManagementScreen } from "@/features/project-management";

vi.mock("@/features/project-management", () => ({
  ProjectManagementScreen: vi.fn(),
}));

describe("home page", () => {
  it("renders the Project Management public screen inside MainLayout", () => {
    const element = HomePage();
    expect(element.type).toBe(MainLayout);
    expect(element.props.children.type).toBe(ProjectManagementScreen);
  });
});
