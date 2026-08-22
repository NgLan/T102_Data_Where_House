"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, type UseFormReturn } from "react-hook-form";
import { handleApiError, isApiError, notifyApiError, type CreateProjectRequest } from "@/api";
import {
  createProjectFormSchema,
  DEFAULT_CREATE_PROJECT_VALUES,
  type CreateProjectFormValues,
} from "../schemas/create-project-form-schema";
import { mapProjectApiFieldErrors } from "../utils/map-project-api-field-errors";

interface CreateProjectFormOptions {
  onOpenChange: (isOpen: boolean) => void;
  onSubmit: (body: CreateProjectRequest) => Promise<unknown>;
}

/** Quản lý form tạo Project bằng React Hook Form và generated Zod contract.
 * @param options Callback đóng dialog và mutation tạo Project.
 * @returns Form API cùng submit/close handlers đã chuẩn hóa.
 */
export function useCreateProjectForm(options: CreateProjectFormOptions) {
  const form = useForm<CreateProjectFormValues, undefined, CreateProjectRequest>({
    resolver: zodResolver(createProjectFormSchema),
    defaultValues: DEFAULT_CREATE_PROJECT_VALUES,
  });
  const handleValidSubmit = async (body: CreateProjectRequest) => {
    try {
      await options.onSubmit(body);
      form.reset();
    } catch (error) {
      handleSubmissionError(error, form, form.getValues("domainSelection"));
    }
  };
  const handleClose = () => {
    if (form.formState.isSubmitting) return;
    form.reset();
    options.onOpenChange(false);
  };
  return { form, handleClose, handleSubmit: form.handleSubmit(handleValidSubmit) };
}

function handleSubmissionError(
  error: unknown,
  form: UseFormReturn<CreateProjectFormValues, undefined, CreateProjectRequest>,
  domainSelection: string,
): void {
  if (!isApiError(error)) {
    handleApiError(error);
    return;
  }
  const unmappedCount = mapProjectApiFieldErrors(error, form.setError, domainSelection);
  if (unmappedCount > 0) notifyApiError(error, true);
}
