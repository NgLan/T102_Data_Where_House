// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/common/errors/api-error";
import { CreateProjectDialog } from "./CreateProjectDialog";

const mocks = vi.hoisted(() => ({ handleApiError: vi.fn() }));

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock("@/common/errors/handle-api-error", () => ({
  handleApiError: mocks.handleApiError,
}));
vi.mock("@/common/components/ui/dialog", () => ({
  Dialog: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DialogContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DialogDescription: ({ children }: { children: React.ReactNode }) => <p>{children}</p>,
  DialogFooter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DialogHeader: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DialogTitle: ({ children }: { children: React.ReactNode }) => <h2>{children}</h2>,
}));

afterEach(cleanup);

describe("CreateProjectDialog", () => {
  it("shows Zod errors and blocks an invalid submission", () => {
    const submit = vi.fn();
    render(<CreateProjectDialog isOpen onOpenChange={vi.fn()} onSubmit={submit} />);
    fireEvent.click(screen.getByRole("button", { name: "CREATE_ACTION" }));
    expect(screen.getByText("ERROR_NAME_MIN")).toBeInTheDocument();
    expect(screen.getByText("ERROR_REQUIREMENT_MIN")).toBeInTheDocument();
    expect(submit).not.toHaveBeenCalled();
  });

  it("maps Backend validation details below the matching field", async () => {
    const error = new ApiError({
      status: 422, errorCode: "VALIDATION_ERROR", message: "invalid",
      details: [{ field: "name", message: "Server name error" }],
      kind: "validation", originalError: null,
    });
    const submit = vi.fn().mockRejectedValue(error);
    render(<CreateProjectDialog isOpen onOpenChange={vi.fn()} onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText("NAME_LABEL"), { target: { value: "Sales" } });
    fireEvent.change(screen.getByLabelText("REQUIREMENT_LABEL"), { target: { value: "Track revenue" } });
    fireEvent.click(screen.getByRole("button", { name: "CREATE_ACTION" }));
    await waitFor(() => expect(screen.getByText("Server name error")).toBeInTheDocument());
  });

  it("reports an unexpected adapter error instead of failing silently", async () => {
    const error = new Error("INVALID_API_RESPONSE");
    const submit = vi.fn().mockRejectedValue(error);
    render(<CreateProjectDialog isOpen onOpenChange={vi.fn()} onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText("NAME_LABEL"), { target: { value: "Sales" } });
    fireEvent.change(screen.getByLabelText("REQUIREMENT_LABEL"), {
      target: { value: "Track revenue" },
    });
    fireEvent.click(screen.getByRole("button", { name: "CREATE_ACTION" }));
    await waitFor(() => expect(mocks.handleApiError).toHaveBeenCalledWith(error));
  });
});
