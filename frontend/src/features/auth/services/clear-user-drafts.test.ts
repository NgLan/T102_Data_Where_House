// @vitest-environment jsdom

import { beforeEach, describe, expect, it } from "vitest";
import { clearUserModelingDrafts } from "./clear-user-drafts";

describe("clearUserModelingDrafts", () => {
  beforeEach(() => window.localStorage.clear());

  it("removes modeling state while preserving language and theme", () => {
    localStorage.setItem("modeling-draft:project-1", "draft");
    localStorage.setItem("modeling-agent-dock:project-1", "open");
    localStorage.setItem("i18nextLng", "vi");
    localStorage.setItem("theme", "dark");

    clearUserModelingDrafts();

    expect(localStorage.getItem("modeling-draft:project-1")).toBeNull();
    expect(localStorage.getItem("modeling-agent-dock:project-1")).toBeNull();
    expect(localStorage.getItem("i18nextLng")).toBe("vi");
    expect(localStorage.getItem("theme")).toBe("dark");
  });
});
