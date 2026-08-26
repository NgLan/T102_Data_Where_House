// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { StructuredRequirementsTable } from "./StructuredRequirementsTable";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
const items = [
  { id: "low", title: "Zulu", description: "Low", type: "BUSINESS" as const, priority: "LOW" as const },
  { id: "high", title: "Alpha", description: "High", type: "ANALYTICAL" as const, priority: "HIGH" as const },
];
afterEach(cleanup);

describe("StructuredRequirementsTable", () => {
  it("is read-only and applies the business default order", () => {
    render(<StructuredRequirementsTable items={items} />);
    expect(firstRow()).toHaveTextContent("Alpha");
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });
  it("sorts all three columns", () => {
    render(<StructuredRequirementsTable items={items} />);
    fireEvent.click(screen.getByRole("button", { name: "TYPE_LABEL" }));
    expect(firstRow()).toHaveTextContent("Zulu");
    fireEvent.click(screen.getByRole("button", { name: "PRIORITY_LABEL" }));
    expect(firstRow()).toHaveTextContent("Alpha");
    fireEvent.click(screen.getByRole("button", { name: "REQUIREMENT_LABEL" }));
    fireEvent.click(screen.getByRole("button", { name: "REQUIREMENT_LABEL" }));
    expect(firstRow()).toHaveTextContent("Zulu");
  });
  it("requires confirmation before deleting one requirement", async () => {
    const onDelete = vi.fn().mockResolvedValue(undefined);
    render(<StructuredRequirementsTable items={items} canDelete onDelete={onDelete} />);
    await userEvent.click(screen.getAllByRole("button", {
      name: "BTN_DELETE_STRUCTURED_REQUIREMENT",
    })[0]);
    expect(onDelete).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "BTN_DELETE" }));
    expect(onDelete).toHaveBeenCalledOnce();
  });
});
function firstRow() { return screen.getAllByRole("row")[1]; }
