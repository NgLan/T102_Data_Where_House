// @vitest-environment jsdom

import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useDraftAutosave } from "./use-draft-autosave";

describe("useDraftAutosave", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("saves exactly five minutes after the latest edit", async () => {
    vi.useFakeTimers();
    const onSave = vi.fn().mockResolvedValue({ revision: 2 });
    const { rerender } = renderHook(
      ({ draftKey }) =>
        useDraftAutosave({ draftKey, isDirty: true, canSave: true, onSave }),
      { initialProps: { draftKey: "first" } },
    );
    await act(async () => vi.advanceTimersByTimeAsync(4 * 60 * 1_000));
    rerender({ draftKey: "second" });
    await act(async () => vi.advanceTimersByTimeAsync(4 * 60 * 1_000));
    expect(onSave).not.toHaveBeenCalled();

    await act(async () => vi.advanceTimersByTimeAsync(60 * 1_000));

    expect(onSave).toHaveBeenCalledOnce();
  });

  it("retries sequentially after a failed save", async () => {
    vi.useFakeTimers();
    vi.spyOn(Math, "random").mockReturnValue(0);
    const onSave = vi
      .fn()
      .mockResolvedValueOnce(null)
      .mockResolvedValueOnce({ revision: 2 });
    renderHook(() =>
      useDraftAutosave({
        draftKey: "draft",
        isDirty: true,
        canSave: true,
        onSave,
      }),
    );
    await act(async () => vi.advanceTimersByTimeAsync(5 * 60 * 1_000));
    expect(onSave).toHaveBeenCalledTimes(1);
    await act(async () => vi.advanceTimersByTimeAsync(2_000));

    expect(onSave).toHaveBeenCalledTimes(2);
    expect(onSave.mock.results[0].type).toBe("return");
  });
});
