// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExecutionLog } from "./ExecutionLog";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock("@/common/notifications", () => ({
  useAppNotification: () => ({ getErrorMessage: (code: string) => `error:${code}` }),
}));

describe("ExecutionLog", () => {
  it("công bố live log và empty state", () => {
    render(<ExecutionLog logs={[]} />);
    expect(screen.getByRole("log")).toHaveAttribute("aria-live", "polite");
    expect(screen.getByText(/MSG_TERMINAL_READY/)).toBeInTheDocument();
  });

  it("dịch local log và error code theo đúng namespace", () => {
    render(<ExecutionLog logs={[
      { id: "one", timestamp: "10:00", type: "success", translationKey: "MSG_EXECUTION_SUMMARY", params: { succeeded: 1, executed: 1, duration: 2 } },
      { id: "two", timestamp: "10:01", type: "error", errorCode: "SANDBOX_EXECUTION_ERROR" },
    ]} />);
    expect(screen.getByText("MSG_EXECUTION_SUMMARY")).toBeInTheDocument();
    expect(screen.getByText("error:SANDBOX_EXECUTION_ERROR")).toBeInTheDocument();
  });
});
