// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ProjectList } from "./ProjectList";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => ({ getErrorMessage: (code: string) => code }),
}));
vi.mock("./ProjectCard", () => ({ ProjectCard: () => <article>project-card</article> }));

afterEach(cleanup);

const BASE_PROPS = {
  projects: [], totalCount: 0, errorCode: "UNKNOWN_ERROR", hasSearchQuery: false,
  isInitialError: false, isInitialLoading: false, deletingProjectIds: new Set<string>(),
  onRetry: vi.fn(), onClearSearch: vi.fn(), onCreateProject: vi.fn(), onDeleteProject: vi.fn(),
};

describe("ProjectList", () => {
  it("hiển thị skeleton ở lần tải đầu", () => {
    const { container } = render(<ProjectList {...BASE_PROPS} isInitialLoading />);
    expect(container.querySelector("[aria-busy='true']")).toBeInTheDocument();
  });

  it("phân biệt empty và no-search-results", () => {
    const { rerender } = render(<ProjectList {...BASE_PROPS} />);
    expect(screen.getByText("TXT_EMPTY_TITLE")).toBeInTheDocument();
    rerender(<ProjectList {...BASE_PROPS} totalCount={2} hasSearchQuery />);
    expect(screen.getByText("TXT_NO_RESULTS_TITLE")).toBeInTheDocument();
  });

  it("hiển thị lỗi có retry", () => {
    render(<ProjectList {...BASE_PROPS} isInitialError errorCode="PROJECT_LIST_FAILED" />);
    expect(screen.getByText("PROJECT_LIST_FAILED")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "BTN_RETRY" })).toBeInTheDocument();
  });
});
