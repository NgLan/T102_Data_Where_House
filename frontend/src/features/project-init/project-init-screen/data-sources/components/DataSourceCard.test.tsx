// @vitest-environment jsdom
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataSourceCard } from "./DataSourceCard";

vi.mock("react-i18next", () => ({ initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }) }));
const source = { id: "source-1", project_id: "project-1", name: "orders.csv", type: "CSV" as const,
  description: null, tables: [], analysis_status: "PENDING" as const };

describe("DataSourceCard", () => {
  it("is collapsed by default and shows pending guidance when expanded", () => {
    render(<DataSourceCard projectId="project-1" source={source} canEdit={false}
      disabled={false} onDelete={vi.fn()} />);
    expect(screen.queryByText("TXT_SOURCE_PENDING_TITLE")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /orders.csv/ }));
    expect(screen.getByText("TXT_SOURCE_PENDING_TITLE")).toBeInTheDocument();
  });
});
