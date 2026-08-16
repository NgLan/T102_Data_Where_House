import { z } from "zod";
import {
  MAX_PROJECT_DOMAIN_LENGTH,
  MAX_PROJECT_NAME_LENGTH,
  MIN_PROJECT_DOMAIN_LENGTH,
  MIN_PROJECT_NAME_LENGTH,
  MIN_PROJECT_REQUIREMENT_LENGTH,
} from "@/common/constants/project-constraints";

/** Schema xác thực form khởi tạo dự án, dùng key i18n làm error message. */
export const projectDetailsSchema = z.object({
  name: z
    .string()
    .trim()
    .min(MIN_PROJECT_NAME_LENGTH, "ERR_PROJECT_NAME_MIN")
    .max(MAX_PROJECT_NAME_LENGTH, "ERR_PROJECT_NAME_MAX"),
  domain: z
    .string()
    .trim()
    .min(MIN_PROJECT_DOMAIN_LENGTH, "ERR_DOMAIN_REQUIRED")
    .max(MAX_PROJECT_DOMAIN_LENGTH, "ERR_DOMAIN_MAX"),
  requirement: z
    .string()
    .trim()
    .min(MIN_PROJECT_REQUIREMENT_LENGTH, "ERR_REQUIREMENT_MIN"),
});

export type ProjectDetailsValues = z.infer<typeof projectDetailsSchema>;
export type ProjectDetailsField = keyof ProjectDetailsValues;
export type ProjectDetailsErrors = Partial<Record<ProjectDetailsField, string>>;
