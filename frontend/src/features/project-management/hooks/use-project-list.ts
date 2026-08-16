"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ProjectSummaryResponse } from "@/api";
import { isApiError } from "@/common/errors/api-error";
import { requestProjects } from "../services/project-management-api";

export type ProjectListStatus =
  | "initial-loading"
  | "ready"
  | "refreshing"
  | "error";

interface ProjectListState {
  projects: ProjectSummaryResponse[];
  status: ProjectListStatus;
  errorCode: string;
}

const UNKNOWN_ERROR_CODE = "UNKNOWN_ERROR";
const INITIAL_STATE: ProjectListState = {
  projects: [],
  status: "initial-loading",
  errorCode: UNKNOWN_ERROR_CODE,
};

/** Quản lý loading, stale request và search của danh sách Project. */
export function useProjectList() {
  const requestSequence = useRef(0);
  const [state, setState] = useState(INITIAL_STATE);
  const [searchQuery, setSearchQuery] = useState("");
  const loadProjects = useCallback(async (isRefresh = false) => {
    const sequence = ++requestSequence.current;
    if (isRefresh) setState((current) => ({ ...current, status: "refreshing" }));
    try {
      const projects = await requestProjects();
      if (sequence !== requestSequence.current) return;
      setState({ projects, status: "ready", errorCode: UNKNOWN_ERROR_CODE });
    } catch (error) {
      if (sequence !== requestSequence.current) return;
      setState((current) => ({
        ...current,
        errorCode: errorCodeOf(error),
        status: current.projects.length > 0 ? "ready" : "error",
      }));
    }
  }, []);
  useEffect(() => {
    void loadProjects();
    return () => { requestSequence.current += 1; };
  }, [loadProjects]);
  const projects = useMemo(
    () => filterProjects(state.projects, searchQuery),
    [searchQuery, state.projects],
  );
  const removeProject = useCallback((projectId: string) => {
    setState((current) => ({
      ...current,
      projects: current.projects.filter((project) => project.id !== projectId),
    }));
  }, []);
  return {
    ...state, projects, searchQuery, setSearchQuery, removeProject,
    refreshProjects: () => loadProjects(true),
    retryProjects: () => loadProjects(false),
    totalCount: state.projects.length,
  };
}

function filterProjects(projects: ProjectSummaryResponse[], query: string) {
  const normalized = query.trim().toLocaleLowerCase();
  if (!normalized) return projects;
  return projects.filter((project) =>
    [project.name, project.domain, project.description].some((value) =>
      value?.toLocaleLowerCase().includes(normalized),
    ),
  );
}

function errorCodeOf(error: unknown): string {
  return isApiError(error) ? error.errorCode : UNKNOWN_ERROR_CODE;
}
