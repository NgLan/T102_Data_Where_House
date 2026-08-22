import { zUpdateProjectRequest } from "@/api";
import { z } from "zod";

/** Giá trị chuỗi mà input HTML sử dụng trước khi chuyển sang contract API nullable. */
export interface ProjectDetailsValues {
  name: string;
  domain: string;
  requirement: string;
}

export type ProjectDetailsField = keyof ProjectDetailsValues;
export type ProjectDetailsErrors = Partial<Record<ProjectDetailsField, string>>;

/** Chuyển giá trị form sang input nullable trước khi gọi generated schema. */
export function parseProjectDetailsForm(values: ProjectDetailsValues) {
  return zUpdateProjectRequest.safeParse({
    name: values.name.trim(),
    domain: values.domain.trim() || null,
    requirement: values.requirement.trim() || null,
  });
}

/** Schema form normalize input HTML rồi chuyển qua generated OpenAPI schema. */
export const projectDetailsFormSchema = z
  .object({
    name: z.string(),
    domain: z.string(),
    requirement: z.string(),
  })
  .superRefine((values, context) => {
    const result = zUpdateProjectRequest.safeParse(
      normalizeProjectDetails(values),
    );
    if (!result.success)
      result.error.issues.forEach((issue) =>
        context.addIssue({
          code: "custom",
          message: projectDetailsIssueKey(issue),
          path: issue.path,
        }),
      );
  });

function normalizeProjectDetails(values: ProjectDetailsValues) {
  return {
    name: values.name.trim(),
    domain: values.domain.trim() || null,
    requirement: values.requirement.trim() || null,
  };
}

/** Ánh xạ issue của generated schema sang key i18n ổn định của form Project Details. */
export function projectDetailsIssueKey(issue: z.core.$ZodIssue): string {
  const field = issue.path[0];
  if (field === "name" && issue.code === "too_small")
    return "MSG_PROJECT_NAME_MIN";
  if (field === "name" && issue.code === "too_big")
    return "MSG_PROJECT_NAME_MAX";
  if (field === "domain" && issue.code === "too_big")
    return "MSG_PROJECT_DOMAIN_MAX";
  if (field === "requirement" && issue.code === "too_small") {
    return "MSG_PROJECT_REQUIREMENT_MIN";
  }
  return "MSG_PROJECT_INVALID";
}
