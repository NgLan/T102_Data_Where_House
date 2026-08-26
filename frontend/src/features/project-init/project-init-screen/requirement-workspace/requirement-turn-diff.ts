import type { ProjectRequirementResponse } from "@/api";

export interface RequirementTurnDiff {
  newIds: readonly string[];
  changedIds: readonly string[];
  deletedTitles: readonly string[];
}

/** So sánh hai canonical snapshots theo stable Requirement identity. */
export function createRequirementTurnDiff(
  before: readonly ProjectRequirementResponse[],
  after: readonly ProjectRequirementResponse[],
): RequirementTurnDiff {
  const previous = new Map(before.map((item) => [item.id, item]));
  const currentIds = new Set(after.map((item) => item.id));
  return {
    newIds: after.filter((item) => !previous.has(item.id)).map((item) => item.id),
    changedIds: after
      .filter((item) => hasChanged(previous.get(item.id), item))
      .map((item) => item.id),
    deletedTitles: before
      .filter((item) => !currentIds.has(item.id))
      .map((item) => item.title),
  };
}

function hasChanged(
  before: ProjectRequirementResponse | undefined,
  after: ProjectRequirementResponse,
): boolean {
  return Boolean(before && (
    before.title !== after.title ||
    before.description !== after.description ||
    before.type !== after.type ||
    before.priority !== after.priority
  ));
}
