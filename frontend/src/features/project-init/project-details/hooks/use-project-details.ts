"use client";

import { useCallback, useEffect, useState } from "react";
import { isApiError } from "@/common/errors/api-error";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import {
  projectDetailsSchema,
  type ProjectDetailsErrors,
  type ProjectDetailsField,
  type ProjectDetailsValues,
} from "../schemas/project-details-schema";
import {
  getProjectDetails,
  updateProjectDetails,
} from "../services/project-service";

const EMPTY_FORM: ProjectDetailsValues = {
  name: "",
  domain: "",
  requirement: "",
};

/** Quản lý form dự án hiện hữu; tạo mới thuộc feature Project Management.
 * @param projectId ID Project cần tải và cập nhật.
 * @returns State form cùng các thao tác tải lại, cập nhật field và lưu.
 */
export function useProjectDetails(projectId: string) {
  const { notifyError, notifySuccess } = useAppNotification();
  const [form, setForm] = useState<ProjectDetailsValues>(EMPTY_FORM);
  const [errors, setErrors] = useState<ProjectDetailsErrors>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const project = await getProjectDetails(projectId);
      setForm({
        name: project.name,
        domain: project.domain ?? "",
        requirement: project.requirement,
      });
    } catch (error) {
      setLoadError(errorCodeOf(error));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    let active = true;
    void getProjectDetails(projectId)
      .then((project) => {
        if (!active) return;
        setForm({
          name: project.name,
          domain: project.domain ?? "",
          requirement: project.requirement,
        });
      })
      .catch((error) => {
        if (active) setLoadError(errorCodeOf(error));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const updateField = useCallback(
    (field: ProjectDetailsField, value: string) => {
      setForm((current) => ({ ...current, [field]: value }));
      setErrors((current) => ({ ...current, [field]: undefined }));
    },
    [],
  );

  const appendRequirement = useCallback((value: string) => {
    setForm((current) => ({
      ...current,
      requirement: [current.requirement.trim(), value.trim()]
        .filter(Boolean)
        .join("\n\n"),
    }));
    setErrors((current) => ({ ...current, requirement: undefined }));
  }, []);

  const save = useCallback(async () => {
    const result = projectDetailsSchema.safeParse(form);
    if (!result.success) {
      setErrors(toFieldErrors(result.error.issues));
      return false;
    }
    setIsSaving(true);
    try {
      await updateProjectDetails(projectId, result.data);
      notifySuccess("MSG_ACTION_COMPLETED");
      return true;
    } catch (error) {
      notifyError(errorCodeOf(error));
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [form, notifyError, notifySuccess, projectId]);

  return {
    appendRequirement,
    errors,
    form,
    isLoading,
    isSaving,
    loadError,
    reload,
    save,
    updateField,
  };
}

function toFieldErrors(
  issues: ReadonlyArray<{ path: PropertyKey[]; message: string }>,
) {
  const errors: ProjectDetailsErrors = {};
  for (const issue of issues) {
    const field = issue.path[0] as ProjectDetailsField;
    if (field in EMPTY_FORM) errors[field] = issue.message;
  }
  return errors;
}

function errorCodeOf(error: unknown): string {
  return isApiError(error) ? error.errorCode : "UNKNOWN_ERROR";
}
