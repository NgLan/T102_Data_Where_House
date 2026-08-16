"use client";

import { useRef, useState, type FormEvent } from "react";
import type { CreateProjectRequest } from "@/api";
import { applyApiFieldErrors } from "@/common/errors/apply-api-field-errors";
import { isApiError } from "@/common/errors/api-error";
import { handleApiError } from "@/common/errors/handle-api-error";
import { DEFAULT_PROJECT_DOMAIN } from "../constants/project-domain-options";
import {
  createProjectFormSchema,
  type CreateProjectFormValues,
} from "../schemas/create-project-form-schema";

export type CreateProjectFormErrors = Partial<
  Record<keyof CreateProjectFormValues, string>
>;

interface CreateProjectFormOptions {
  onOpenChange: (isOpen: boolean) => void;
  onSubmit: (body: CreateProjectRequest) => Promise<void>;
  translateError: (key: string) => string;
}

const INITIAL_VALUES: CreateProjectFormValues = {
  name: "",
  domain: DEFAULT_PROJECT_DOMAIN,
  requirement: "",
};
const PROJECT_FIELDS = new Set(Object.keys(INITIAL_VALUES));

/** Quản lý lifecycle, Zod validation và Backend field errors của create form. */
export function useCreateProjectForm(options: CreateProjectFormOptions) {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState<CreateProjectFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSubmittingRef = useRef(false);

  const handleFieldChange = (field: keyof CreateProjectFormValues, value: string) => {
    setValues((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
  };
  const handleClose = () => {
    if (isSubmittingRef.current) return;
    resetForm(setValues, setErrors);
    options.onOpenChange(false);
  };
  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSubmittingRef.current) return;
    const parsed = createProjectFormSchema.safeParse(values);
    if (!parsed.success) {
      setErrors(toFormErrors(parsed.error.issues, options.translateError));
      return;
    }
    isSubmittingRef.current = true;
    setIsSubmitting(true);
    try {
      await options.onSubmit(parsed.data);
      resetForm(setValues, setErrors);
    } catch (error) {
      if (isApiError(error)) mapServerErrors(error, setErrors);
      else handleApiError(error);
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  };
  return { errors, handleClose, handleFieldChange, handleSubmit, isSubmitting, values };
}

type ErrorSetter = React.Dispatch<React.SetStateAction<CreateProjectFormErrors>>;
type ValueSetter = React.Dispatch<React.SetStateAction<CreateProjectFormValues>>;

function resetForm(setValues: ValueSetter, setErrors: ErrorSetter): void {
  setValues(INITIAL_VALUES);
  setErrors({});
}

function mapServerErrors(error: Parameters<typeof applyApiFieldErrors>[0], setErrors: ErrorSetter) {
  applyApiFieldErrors(error, {
    resolveField: resolveProjectField,
    setError: (field, detail) => {
      setErrors((current) => ({ ...current, [field]: detail.message }));
    },
  });
}

function toFormErrors(
  issues: ReadonlyArray<{ path: PropertyKey[]; message: string }>,
  translate: (key: string) => string,
): CreateProjectFormErrors {
  return Object.fromEntries(
    issues.map((issue) => [issue.path[0], translate(issue.message)]),
  );
}

function resolveProjectField(path: string): keyof CreateProjectFormValues | null {
  const field = path.split(".").at(-1) ?? "";
  return PROJECT_FIELDS.has(field) ? (field as keyof CreateProjectFormValues) : null;
}
