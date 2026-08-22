// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/api";
import { CreateProjectDialog } from "./CreateProjectDialog";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
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
  it("gửi description thay requirement và reset sau thành công", async () => {
    const submit = vi.fn().mockResolvedValue(undefined);
    render(<CreateProjectDialog isOpen onOpenChange={vi.fn()} onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText("NAME_LABEL"), { target: { value: "Sales DWH" } });
    fireEvent.change(screen.getByLabelText("DESCRIPTION_LABEL"), {
      target: { value: "Sales analytics" },
    });
    fireEvent.click(screen.getByRole("button", { name: "BTN_CREATE_ACTION" }));
    await waitFor(() => expect(submit).toHaveBeenCalledWith({
      name: "Sales DWH", domain: "ride", description: "Sales analytics",
    }));
    expect(screen.getByLabelText("NAME_LABEL")).toHaveValue("");
  });

  it("giữ dialog và map server field error khi request thất bại", async () => {
    const submit = vi.fn().mockRejectedValue(new ApiError({
      status: 422, errorCode: "VALIDATION_ERROR", message: "invalid",
      details: [{ field: "name", message: "Server name error" }],
      kind: "validation", originalError: null,
    }));
    const onOpenChange = vi.fn();
    render(<CreateProjectDialog isOpen onOpenChange={onOpenChange} onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText("NAME_LABEL"), { target: { value: "Sales" } });
    fireEvent.click(screen.getByRole("button", { name: "BTN_CREATE_ACTION" }));
    expect(await screen.findByText("Server name error")).toBeInTheDocument();
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
  });

  it("reset form khi đóng bằng nút hủy", () => {
    const onOpenChange = vi.fn();
    render(<CreateProjectDialog isOpen onOpenChange={onOpenChange} onSubmit={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("NAME_LABEL"), { target: { value: "Draft" } });
    fireEvent.click(screen.getByRole("button", { name: "BTN_CANCEL" }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(screen.getByLabelText("NAME_LABEL")).toHaveValue("");
  });
});
