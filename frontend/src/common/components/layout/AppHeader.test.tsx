// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AppHeader } from "./AppHeader";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { ProjectSwitcher } from "./ProjectSwitcher";
import { ThemeSwitcher } from "./ThemeSwitcher";
import { UserMenu } from "./UserMenu";

const mocks = vi.hoisted(() => ({
  push: vi.fn(), changeLanguage: vi.fn(), setTheme: vi.fn(), language: "vi",
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock("next-themes", () => ({ useTheme: () => ({ resolvedTheme: "dark", setTheme: mocks.setTheme }) }));
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { resolvedLanguage: mocks.language, changeLanguage: mocks.changeLanguage },
  }),
}));
vi.mock("@/common/projects/project-queries", () => ({
  useAccessibleProjectsQuery: () => ({
    data: [{ id: "project-1", name: "Revenue DWH" }], status: "success",
    isPending: false, isError: false,
  }),
  useCurrentActorQuery: () => ({
    data: { id: "actor-1", username: "MVP Actor", email: "actor@example.com" },
    isPending: false,
  }),
}));

afterEach(cleanup);

describe("header controls", () => {
  beforeEach(() => {
    mocks.push.mockReset();
    mocks.changeLanguage.mockReset();
    mocks.setTheme.mockReset();
    mocks.language = "vi";
  });

  it("chuyển project về workspace mặc định", () => {
    render(<ProjectSwitcher />);
    fireEvent.change(screen.getByLabelText("PROJECT_SELECTOR_LABEL"), {
      target: { value: "project-1" },
    });
    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1");
  });

  it("chuyển ngôn ngữ và theme", () => {
    render(<><LanguageSwitcher /><ThemeSwitcher /></>);
    fireEvent.click(screen.getByRole("button", { name: "BTN_SWITCH_LANGUAGE" }));
    fireEvent.click(screen.getByRole("button", { name: "BTN_SWITCH_THEME" }));
    expect(mocks.changeLanguage).toHaveBeenCalledWith("en");
    expect(mocks.setTheme).toHaveBeenCalledWith("light");
  });

  it("hiển thị actor MVP và logout disabled", () => {
    render(<UserMenu />);
    fireEvent.pointerDown(screen.getByRole("button", { name: /MVP Actor/ }), {
      button: 0, ctrlKey: false,
    });
    expect(screen.getAllByText("MVP Actor").length).toBeGreaterThan(0);
    expect(screen.getByText("BTN_LOGOUT_UNAVAILABLE").closest("[data-disabled]"))
      .toBeInTheDocument();
  });

  it("logo có cursor và quay về danh sách Project", () => {
    render(<AppHeader selectedProjectId="project-1" />);
    const logo = screen.getByRole("link", { name: /TXT_APP_NAME/ });
    expect(logo).toHaveAttribute("href", "/");
    expect(logo).toHaveClass("cursor-pointer");
    expect(screen.getByLabelText("PROJECT_SELECTOR_LABEL")).toHaveValue("project-1");
  });
});
