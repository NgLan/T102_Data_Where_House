import { zCreateProjectRequest, type CreateProjectRequest } from "@/api";
import { z } from "zod";
import {
  CUSTOM_PROJECT_DOMAIN,
  DEFAULT_PROJECT_DOMAIN,
} from "@/common/projects/project-domain-options";

const FORM_INPUT_SCHEMA = z.object({
  name: z.string(),
  domainSelection: z.string(),
  customDomain: z.string(),
  description: z.string(),
});

/** Giá trị thô của form trước khi transform thành request API. */
export interface CreateProjectFormValues {
  name: string;
  domainSelection: string;
  customDomain: string;
  description: string;
}

/** Schema form UI, kiểm tra payload cuối bằng generated OpenAPI schema. */
export const createProjectFormSchema = FORM_INPUT_SCHEMA
  .superRefine(validateCreateProjectValues)
  .transform(toCreateProjectRequest);

/** Giá trị mặc định giữ domain Ride-hailing như hành vi trước refactor. */
export const DEFAULT_CREATE_PROJECT_VALUES: CreateProjectFormValues = {
  name: "",
  domainSelection: DEFAULT_PROJECT_DOMAIN,
  customDomain: "",
  description: "",
};

function validateCreateProjectValues(
  values: CreateProjectFormValues,
  context: z.RefinementCtx,
): void {
  if (values.domainSelection === CUSTOM_PROJECT_DOMAIN && !values.customDomain.trim()) {
    context.addIssue({ code: "custom", path: ["customDomain"], message: "MSG_CUSTOM_DOMAIN_REQUIRED" });
    return;
  }
  const result = zCreateProjectRequest.safeParse(toCreateProjectRequest(values));
  if (result.success) return;
  for (const issue of result.error.issues) {
    context.addIssue({
      code: "custom",
      path: [resolveFormField(String(issue.path[0]), values.domainSelection)],
      message: resolveIssueKey(issue),
    });
  }
}

function toCreateProjectRequest(values: CreateProjectFormValues): CreateProjectRequest {
  const selectedDomain = values.domainSelection === CUSTOM_PROJECT_DOMAIN
    ? values.customDomain.trim()
    : values.domainSelection;
  return {
    name: values.name.trim(),
    domain: selectedDomain || null,
    description: values.description.trim() || null,
  };
}

function resolveFormField(field: string, domainSelection: string): keyof CreateProjectFormValues {
  if (field === "domain") {
    return domainSelection === CUSTOM_PROJECT_DOMAIN ? "customDomain" : "domainSelection";
  }
  return field === "description" ? "description" : "name";
}

function resolveIssueKey(issue: z.core.$ZodIssue): string {
  if (issue.path[0] === "name" && issue.code === "too_small") return "MSG_PROJECT_NAME_MIN";
  if (issue.path[0] === "name" && issue.code === "too_big") return "MSG_PROJECT_NAME_MAX";
  if (issue.path[0] === "domain" && issue.code === "too_big") return "MSG_PROJECT_DOMAIN_MAX";
  return "MSG_PROJECT_INVALID";
}
