"use client";

import { useMemo, useState } from "react";
import type { ProjectSummaryResponse } from "@/api";

/** Quản lý tìm kiếm client-side trên dữ liệu Project đã cache.
 * @param projects Danh sách Project chưa lọc.
 * @returns Query text, setter và danh sách phù hợp.
 */
export function useProjectSearch(projects: ProjectSummaryResponse[]) {
  const [searchQuery, setSearchQuery] = useState("");
  const filteredProjects = useMemo(
    () => filterProjects(projects, searchQuery),
    [projects, searchQuery],
  );
  return { filteredProjects, searchQuery, setSearchQuery };
}

function filterProjects(
  projects: ProjectSummaryResponse[],
  searchQuery: string,
): ProjectSummaryResponse[] {
  const normalizedQuery = searchQuery.trim().toLocaleLowerCase();
  if (!normalizedQuery) return projects;
  return projects.filter((project) =>
    [project.name, project.domain, project.description].some((value) =>
      value?.toLocaleLowerCase().includes(normalizedQuery)));
}
