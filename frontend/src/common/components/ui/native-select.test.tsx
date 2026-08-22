// @vitest-environment jsdom

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NativeSelect, NativeSelectOption } from "./native-select";

describe("NativeSelect", () => {
  it("phát change của select gốc", () => {
    const onChange = vi.fn();
    render(
      <NativeSelect aria-label="type" onChange={onChange}>
        <NativeSelectOption value="int">int</NativeSelectOption>
        <NativeSelectOption value="uuid">uuid</NativeSelectOption>
      </NativeSelect>,
    );
    fireEvent.change(screen.getByLabelText("type"), { target: { value: "uuid" } });
    expect(onChange).toHaveBeenCalledOnce();
  });
});
