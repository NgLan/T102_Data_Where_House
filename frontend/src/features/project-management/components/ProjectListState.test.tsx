// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ProjectListState } from "./ProjectListState";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock("./ProjectCard", () => ({ ProjectCard: ({ project }: { project: { name: string } }) => <div>{project.name}</div> }));

const base = {
  projects: [], totalCount: 0, status: "ready" as const, errorCode: "DATABASE_ERROR",
  hasSearch: false, deletingIds: new Set<string>(), onRetry: vi.fn(),
  onClearSearch: vi.fn(), onCreate: vi.fn(), onDelete: vi.fn(),
};

afterEach(cleanup);

describe("ProjectListState", () => {
  it("distinguishes initial loading, load error, true empty and search empty", () => {
    const { rerender } = render(<ProjectListState {...base} status="initial-loading" />);
    expect(document.querySelector('[aria-busy="true"]')).toBeInTheDocument();
    rerender(<ProjectListState {...base} status="error" />);
    fireEvent.click(screen.getByRole("button", { name: "RETRY" }));
    expect(base.onRetry).toHaveBeenCalledOnce();
    rerender(<ProjectListState {...base} />);
    expect(screen.getByText("EMPTY_TITLE")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "CREATE_PROJECT" }));
    expect(base.onCreate).toHaveBeenCalledOnce();
    rerender(<ProjectListState {...base} totalCount={2} hasSearch />);
    expect(screen.getByText("NO_RESULTS_TITLE")).toBeInTheDocument();
  });
});
