import { z } from "zod";

type Translate = (key: string) => string;

export function createLoginSchema(t: Translate) {
  return z.object({
    identifier: z.string().trim().min(3, t("MSG_IDENTIFIER_REQUIRED")),
    password: z.string().min(1, t("MSG_PASSWORD_REQUIRED")),
  });
}

export function createRegisterSchema(t: Translate) {
  return z.object({
    username: z.string().trim().min(3, t("MSG_USERNAME_MIN")).max(100),
    email: z.email(t("MSG_EMAIL_INVALID")),
    full_name: z.string().trim().max(150).optional(),
    password: z.string()
      .min(12, t("MSG_PASSWORD_POLICY"))
      .max(72, t("MSG_PASSWORD_POLICY"))
      .regex(/[A-Za-z]/, t("MSG_PASSWORD_POLICY"))
      .regex(/\d/, t("MSG_PASSWORD_POLICY")),
  });
}

export type LoginFormValues = z.infer<ReturnType<typeof createLoginSchema>>;
export type RegisterFormValues = z.infer<ReturnType<typeof createRegisterSchema>>;
