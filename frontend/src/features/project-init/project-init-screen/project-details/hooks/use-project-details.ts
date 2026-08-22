"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useAppNotification } from "@/common/notifications";
import { PROJECTS_QUERY_KEY } from "@/common/projects/project-queries";
import { projectInitQueryKeys } from "../../../constants/project-init-query-keys";
import {
  parseProjectDetailsForm,
  projectDetailsFormSchema,
  type ProjectDetailsValues,
} from "../schemas/project-details-schema";
import {
  getProjectDetails,
  updateProjectDetails,
} from "../services/project-details-api";

const EMPTY_FORM: ProjectDetailsValues = {
  name: "",
  domain: "",
  requirement: "",
};

/** Quản lý Project form bằng React Hook Form và TanStack Query. */
export function useProjectDetails(projectId: string) {
  const queryClient = useQueryClient();
  const { notifySuccess } = useAppNotification();
  const form = useForm<ProjectDetailsValues>({
    defaultValues: EMPTY_FORM,
    resolver: zodResolver(projectDetailsFormSchema),
  });
  const projectQuery = useQuery({
    queryKey: projectInitQueryKeys.project(projectId),
    queryFn: () => getProjectDetails(projectId),
  });
  useEffect(() => {
    if (projectQuery.data && !form.formState.isDirty) {
      form.reset(toFormValues(projectQuery.data));
    }
  }, [form, form.formState.isDirty, projectQuery.data]);
  const updateMutation = useMutation({
    mutationKey: ["update-project-details", projectId],
    mutationFn: (values: ProjectDetailsValues) =>
      updateProject(projectId, values),
    onSuccess: async (project) => {
      form.reset(toFormValues(project));
      queryClient.setQueryData(
        projectInitQueryKeys.project(projectId),
        project,
      );
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY }),
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.status(projectId),
        }),
      ]);
      notifySuccess("MSG_PROJECT_DETAILS_SAVED");
    },
  });
  const save = async (): Promise<boolean> => {
    if (!form.formState.isDirty) return true;
    if (!(await form.trigger())) return false;
    await updateMutation.mutateAsync(form.getValues());
    return true;
  };
  return { form, projectQuery, save, updateMutation };
}

async function updateProject(projectId: string, values: ProjectDetailsValues) {
  const parsed = parseProjectDetailsForm(values);
  if (!parsed.success) throw parsed.error;
  return updateProjectDetails(projectId, parsed.data);
}

function toFormValues(project: {
  name: string;
  domain: string | null;
  requirement: string | null;
}): ProjectDetailsValues {
  return {
    name: project.name,
    domain: project.domain ?? "",
    requirement: project.requirement ?? "",
  };
}
