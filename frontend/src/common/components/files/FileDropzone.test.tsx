// @vitest-environment jsdom
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FileDropzone } from "./FileDropzone";

describe("FileDropzone", () => {
  it("makes the whole area clickable and accepts a dropped CSV", async () => {
    const onAccept = vi.fn();
    const { container } = render(<FileDropzone accept={{ "text/csv": [".csv"] }}
      title="Upload CSV" help="Drop here" multiple onAccept={onAccept} onReject={vi.fn()} />);
    const input = container.querySelector("input") as HTMLInputElement;
    const click = vi.spyOn(input, "click");
    fireEvent.click(screen.getByRole("button", { name: "Upload CSV" }));
    expect(click).toHaveBeenCalled();
    const file = new File(["id\n1"], "data.csv", { type: "text/csv" });
    fireEvent.change(input, { target: { files: [file] } });
    await waitFor(() => expect(onAccept).toHaveBeenCalled());
    expect(onAccept.mock.calls[0][0]).toEqual([file]);
  });
});
