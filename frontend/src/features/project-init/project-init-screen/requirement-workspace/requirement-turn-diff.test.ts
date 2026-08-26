import { describe, expect, it } from "vitest";
import type { ProjectRequirementResponse } from "@/api";
import { createRequirementTurnDiff } from "./requirement-turn-diff";

const requirement = (
  id: string, title: string, description = "Mô tả",
): ProjectRequirementResponse => ({
  id, title, description, type: "ANALYTICAL", priority: "MEDIUM",
});

describe("createRequirementTurnDiff", () => {
  it("nhận diện item mới, thay đổi và bị xóa theo stable ID", () => {
    const result = createRequirementTurnDiff(
      [requirement("same", "Giữ nguyên"), requirement("changed", "Tên cũ"), requirement("deleted", "Đã xóa")],
      [requirement("same", "Giữ nguyên"), requirement("changed", "Tên mới"), requirement("new", "Mới")],
    );

    expect(result.newIds).toEqual(["new"]);
    expect(result.changedIds).toEqual(["changed"]);
    expect(result.deletedTitles).toEqual(["Đã xóa"]);
  });
});
