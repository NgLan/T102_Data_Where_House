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
  saveRawRequirement,
  updateProjectDetails,
} from "../services/project-details-api";

const EMPTY_FORM: ProjectDetailsValues = {
  name: "",
  domain: "",
  description: "",
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
      form.resetField("name", { defaultValue: project.name });
      form.resetField("domain", { defaultValue: project.domain ?? "" });
      form.resetField("description", { defaultValue: project.description ?? "" });
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
    },
  });
  const rawRequirementMutation = useMutation({
    mutationKey: ["save-raw-requirement", projectId],
    mutationFn: (input: { requirement: string; expectedRevision: number }) =>
      saveRawRequirement(
        projectId,
        input.requirement,
        input.expectedRevision,
      ),
    onSuccess: async (raw) => {
      if (!raw) return;
      form.resetField("requirement", {
        defaultValue: raw.requirement ?? "",
      });
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.project(projectId),
        }),
        queryClient.invalidateQueries({
          queryKey: projectInitQueryKeys.clarification(projectId),
        }),
      ]);
    },
  });
  const persistDraft = async (shouldNotify: boolean): Promise<boolean> => {
    if (!(await form.trigger())) return false;
    const values = form.getValues();
    const updated = await updateMutation.mutateAsync(values);
    const raw = await rawRequirementMutation.mutateAsync({
      requirement: values.requirement,
      expectedRevision: updated.requirement_revision,
    });
    form.reset(toFormValues({ ...updated, requirement: raw.requirement }));
    await queryClient.invalidateQueries({
      queryKey: projectInitQueryKeys.clarification(projectId),
    });
    if (shouldNotify) notifySuccess("MSG_PROJECT_DRAFT_SAVED");
    return true;
  };
  return {
    form,
    projectQuery,
    saveDraft: () => persistDraft(true),
    saveInputsForWorkflow: () => persistDraft(false),
    updateMutation,
    rawRequirementMutation,
    isInfoDirty: Boolean(
      form.formState.dirtyFields.name ||
        form.formState.dirtyFields.domain ||
        form.formState.dirtyFields.description,
    ),
    isRequirementDirty: Boolean(form.formState.dirtyFields.requirement),
  };
}

async function updateProject(projectId: string, values: ProjectDetailsValues) {
  const parsed = parseProjectDetailsForm(values);
  if (!parsed.success) throw parsed.error;
  return updateProjectDetails(projectId, parsed.data);
}

function toFormValues(project: {
  name: string;
  domain: string | null;
  description: string | null;
  requirement: string | null;
}): ProjectDetailsValues {
  return {
    name: project.name,
    domain: project.domain ?? "",
    description: project.description ?? "",
    requirement: project.requirement ?? "",
  };
}
