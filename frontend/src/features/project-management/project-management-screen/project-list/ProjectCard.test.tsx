// @vitest-environment jsdom

import type { ReactNode } from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ProjectSummaryResponse } from "@/api";
import { ProjectCard } from "./ProjectCard";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => <a href={href}>{children}</a>,
}));
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: { count?: number }) => options?.count === undefined
      ? key : `${key}:${options.count}`,
    i18n: { resolvedLanguage: "en" },
  }),
}));

afterEach(cleanup);

function project(overrides: Partial<ProjectSummaryResponse> = {}): ProjectSummaryResponse {
  return {
    id: "project-1", name: "Revenue DWH", user_id: "user-1", status: "ACTIVE",
    domain: "ride", description: "Revenue description", created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z", data_source_count: 2,
    is_data_model_outdated: false, ...overrides,
  };
}

describe("ProjectCard", () => {
  it("hiển thị description ngay dưới tên", () => {
    render(<ProjectCard project={project()} isDeleting={false} onDeleteProject={vi.fn()} />);
    expect(screen.getByRole("heading", { name: "Revenue DWH" }).nextElementSibling)
      .toHaveTextContent("Revenue description");
  });

  it("chỉ hiển thị badge cảnh báo khi Data Model outdated", () => {
    const { rerender } = render(<ProjectCard project={project()} isDeleting={false}
      onDeleteProject={vi.fn()} />);
    expect(screen.queryByText("TXT_DBML_OUTDATED")).not.toBeInTheDocument();
    rerender(<ProjectCard project={project({ is_data_model_outdated: true })}
      isDeleting={false} onDeleteProject={vi.fn()} />);
    expect(screen.getByText("TXT_DBML_OUTDATED")).toBeInTheDocument();
  });
});
