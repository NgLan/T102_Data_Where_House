// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Dialog, DialogContent, DialogTitle } from "./dialog";

describe("DialogContent", () => {
  it("dùng accessible label do consumer truyền cho nút đóng", () => {
    render(
      <Dialog open>
        <DialogContent closeLabel="Đóng hộp thoại">
          <DialogTitle>Title</DialogTitle>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByRole("button", { name: "Đóng hộp thoại" })).toBeInTheDocument();
  });
});
