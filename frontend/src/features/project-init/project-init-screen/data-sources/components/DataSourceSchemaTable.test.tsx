// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataSourceSchemaTable } from "./DataSourceSchemaTable";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

describe("DataSourceSchemaTable", () => {
  it("shows inferred properties and category values read-only", () => {
    render(<DataSourceSchemaTable table={{ name: "orders", columns: [{ name: "status", data_type: "CATEGORY",
      nullable: true, primary_key: false, is_unique_candidate: true, is_key_candidate: false,
      distinct_values: ["new", "done"] }] }} />);
    expect(screen.getByText(/TXT_NULLABLE/)).toHaveTextContent("new, done");
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    expect(screen.getAllByRole("columnheader")).toHaveLength(3);
  });
});
