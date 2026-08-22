// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import { describe, expect, it, vi } from "vitest";
import type { ProjectDetailsValues } from "../schemas/project-details-schema";
import { RawRequirementField } from "./RawRequirementField";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

function Harness() {
  const form = useForm<ProjectDetailsValues>({ defaultValues: { name: "Demo", domain: "", requirement:
    "# Heading\n\n- item\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n<script>alert('x')</script>" } });
  return <RawRequirementField control={form.control} disabled={false} />;
}

describe("RawRequirementField", () => {
  it("renders GFM and never executes raw HTML", async () => {
    const { container } = render(<Harness />);
    await userEvent.click(screen.getByRole("tab", { name: "TXT_REQUIREMENT_PREVIEW_TAB" }));
    expect(screen.getByRole("heading", { name: "Heading" })).toBeInTheDocument();
    expect(screen.getByRole("listitem")).toHaveTextContent("item");
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(container.querySelector("script")).toBeNull();
  });
});
