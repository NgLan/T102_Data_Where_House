"use client";

import { useState } from "react";
import { useProjectList } from "./use-project-list";
import { useProjectMutations } from "./use-project-mutations";

export type { ProjectListStatus } from "./use-project-list";

/** Quản lý lifecycle, mutation và chống stale response của Project Management. */
export function useProjectManagement() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const { removeProject, ...list } = useProjectList();
  const mutations = useProjectMutations({
    onCreated: () => setIsCreateOpen(false),
    onDeleted: removeProject,
  });
  return {
    ...list,
    ...mutations,
    isCreateOpen, setIsCreateOpen,
  };
}
