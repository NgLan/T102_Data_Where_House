// @vitest-environment jsdom

import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { requestDraftValidation } from "../services/draft-validation-api";
import { useDraftValidation } from "./use-draft-validation";

vi.mock("../services/draft-validation-api", () => ({
  requestDraftValidation: vi.fn(),
}));

describe("useDraftValidation", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("validates only after 500 ms of inactivity", async () => {
    vi.useFakeTimers();
    vi.mocked(requestDraftValidation).mockResolvedValue([]);
    renderHook(() =>
      useDraftValidation("project-1", "Table users { id int [pk] }", null),
    );

    await act(async () => vi.advanceTimersByTimeAsync(499));
    expect(requestDraftValidation).not.toHaveBeenCalled();
    await act(async () => vi.advanceTimersByTimeAsync(1));

    expect(requestDraftValidation).toHaveBeenCalledOnce();
  });

  it("ignores a response belonging to an older draft", async () => {
    vi.useFakeTimers();
    let resolveFirst: (value: never[]) => void = () => undefined;
    vi.mocked(requestDraftValidation)
      .mockReturnValueOnce(new Promise((resolve) => { resolveFirst = resolve; }))
      .mockResolvedValueOnce([]);
    const { result, rerender } = renderHook(
      ({ dbml }) => useDraftValidation("project-1", dbml, null),
      { initialProps: { dbml: "Table first { id int [pk] }" } },
    );
    await act(async () => vi.advanceTimersByTimeAsync(500));
    rerender({ dbml: "Table second { id int [pk] }" });
    await act(async () => vi.advanceTimersByTimeAsync(500));
    await act(async () => resolveFirst([]));

    expect(result.current.issues).toEqual([]);
    expect(requestDraftValidation).toHaveBeenCalledTimes(2);
  });
});
