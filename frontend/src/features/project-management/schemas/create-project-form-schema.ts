import { z } from "zod";
import {
  MAX_PROJECT_DOMAIN_LENGTH,
  MAX_PROJECT_NAME_LENGTH,
  MIN_PROJECT_DOMAIN_LENGTH,
  MIN_PROJECT_NAME_LENGTH,
  MIN_PROJECT_REQUIREMENT_LENGTH,
} from "@/common/constants/project-constraints";

/** Giá trị form tạo Project độc lập với transport envelope. */
export const createProjectFormSchema = z.object({
  name: z.string().trim()
    .min(MIN_PROJECT_NAME_LENGTH, "ERROR_NAME_MIN")
    .max(MAX_PROJECT_NAME_LENGTH, "ERROR_NAME_MAX"),
  domain: z
    .string()
    .trim()
    .min(MIN_PROJECT_DOMAIN_LENGTH, "ERROR_DOMAIN_REQUIRED")
    .max(MAX_PROJECT_DOMAIN_LENGTH, "ERROR_DOMAIN_MAX"),
  requirement: z.string().trim()
    .min(MIN_PROJECT_REQUIREMENT_LENGTH, "ERROR_REQUIREMENT_MIN"),
});

export type CreateProjectFormValues = z.infer<typeof createProjectFormSchema>;
