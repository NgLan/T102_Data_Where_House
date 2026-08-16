"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { CreateProjectRequest } from "@/api";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import {
  requestProjectCreation,
  requestProjectDeletion,
} from "../services/project-management-api";

interface ProjectMutationOptions {
  onCreated: () => void;
  onDeleted: (projectId: string) => void;
}

/** Quản lý create/delete Project và trạng thái chống submit lặp. */
export function useProjectMutations(options: ProjectMutationOptions) {
  const router = useRouter();
  const { notifySuccess } = useAppNotification();
  const deletingIdsRef = useRef(new Set<string>());
  const [deletingIds, setDeletingIds] = useState<ReadonlySet<string>>(new Set());
  const createProject = async (body: CreateProjectRequest) => {
    const project = await requestProjectCreation(body);
    notifySuccess("MSG_PROJECT_CREATED");
    options.onCreated();
    router.push(`/projects/${project.id}`);
  };
  const deleteProject = async (projectId: string) => {
    if (deletingIdsRef.current.has(projectId)) return;
    deletingIdsRef.current.add(projectId);
    setDeletingIds(new Set(deletingIdsRef.current));
    try {
      await requestProjectDeletion(projectId);
      options.onDeleted(projectId);
      notifySuccess("MSG_PROJECT_DELETED");
    } finally {
      deletingIdsRef.current.delete(projectId);
      setDeletingIds(new Set(deletingIdsRef.current));
    }
  };
  return { createProject, deleteProject, deletingIds };
}
