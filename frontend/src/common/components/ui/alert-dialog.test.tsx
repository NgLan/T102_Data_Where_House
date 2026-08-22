// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogTitle } from "./alert-dialog";

describe("AlertDialog", () => {
  it("kích hoạt action bằng bàn phím", async () => {
    const onConfirm = vi.fn();
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogTitle>Confirm</AlertDialogTitle>
          <AlertDialogAction onClick={onConfirm}>Continue</AlertDialogAction>
        </AlertDialogContent>
      </AlertDialog>,
    );
    screen.getByRole("button", { name: "Continue" }).focus();
    await userEvent.keyboard("{Enter}");
    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
