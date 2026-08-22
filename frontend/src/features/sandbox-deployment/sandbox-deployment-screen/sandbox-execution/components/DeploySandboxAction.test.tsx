// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DeploySandboxAction } from "./DeploySandboxAction";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

afterEach(cleanup);

const baseProps = {
  isDisabled: false,
  isExecuting: false,
  isSchemaProtected: false,
  schemaName: "sandbox",
  shouldResetSchema: false,
  onExecute: vi.fn(),
  onShouldResetSchemaChange: vi.fn(),
};

describe("DeploySandboxAction", () => {
  it("execute ngay khi không reset schema", () => {
    const onExecute = vi.fn();
    render(<DeploySandboxAction {...baseProps} onExecute={onExecute} />);
    fireEvent.click(screen.getByRole("button", { name: "BTN_DEPLOY" }));
    expect(onExecute).toHaveBeenCalledOnce();
  });

  it("yêu cầu xác nhận trước destructive reset", () => {
    const onExecute = vi.fn();
    render(<DeploySandboxAction {...baseProps} shouldResetSchema onExecute={onExecute} />);
    fireEvent.click(screen.getByRole("button", { name: "BTN_DEPLOY" }));
    expect(onExecute).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "BTN_RESET_AND_EXECUTE" }));
    expect(onExecute).toHaveBeenCalledOnce();
  });

  it("khóa reset cho schema public", () => {
    render(<DeploySandboxAction {...baseProps} isSchemaProtected shouldResetSchema schemaName="PUBLIC" />);
    expect(screen.getByRole("checkbox")).toBeDisabled();
    expect(screen.getByText("TXT_PUBLIC_SCHEMA_PROTECTED")).toBeInTheDocument();
  });
});
