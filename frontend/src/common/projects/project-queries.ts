"use client";

import { queryOptions, useQuery } from "@tanstack/react-query";
import { getAccessibleProjects, getCurrentActorProfile } from "./project-api";

/** Query key ổn định cho danh sách Project dùng chung. */
export const PROJECTS_QUERY_KEY = ["projects"] as const;

/** Query key ổn định cho actor MVP hiện tại. */
export const CURRENT_ACTOR_QUERY_KEY = ["current-actor"] as const;

/** Tạo query options dùng chung cho danh sách Project.
 * @returns Query options có key và query function ổn định.
 */
export function accessibleProjectsQueryOptions() {
  return queryOptions({ queryKey: PROJECTS_QUERY_KEY, queryFn: getAccessibleProjects });
}

/** Đọc danh sách Project từ shared TanStack Query cache.
 * @returns Query result của danh sách Project.
 */
export function useAccessibleProjectsQuery() {
  return useQuery(accessibleProjectsQueryOptions());
}

/** Đọc actor MVP từ shared TanStack Query cache.
 * @returns Query result của actor hiện tại.
 */
export function useCurrentActorQuery() {
  return useQuery({
    queryKey: CURRENT_ACTOR_QUERY_KEY,
    queryFn: getCurrentActorProfile,
    retry: false,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
