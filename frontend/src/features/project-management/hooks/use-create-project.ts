"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAppNotification } from "@/common/notifications";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { createProject } from "../services/project-mutations-api";

interface UseCreateProjectOptions {
  onCreated: () => void;
}

/** Tạo Project, thông báo thành công và mở workspace mới.
 * @param options Callback đóng UI tạo Project.
 * @returns TanStack mutation cho create operation.
 */
export function useCreateProject({ onCreated }: UseCreateProjectOptions) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { notifySuccess } = useAppNotification();
  return useMutation({
    mutationKey: ["create-project"],
    mutationFn: createProject,
    onSuccess: async (project) => {
      await queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY });
      notifySuccess("MSG_PROJECT_CREATED");
      onCreated();
      router.push(`/projects/${project.id}`);
    },
  });
}
