"use client";

import { useMemo } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useRouter } from "next/navigation";
import { handleApiError, resolveApiErrorMessage } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import { CURRENT_ACTOR_QUERY_KEY } from "@/common/projects/project-queries";
import { createLoginSchema, type LoginFormValues } from "../schemas/auth-schemas";
import { loginUser } from "../services/auth-api";

interface LoginFormProps {
  defaultIdentifier?: string;
}

export function LoginForm({ defaultIdentifier = "" }: LoginFormProps) {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const queryClient = useQueryClient();
  const schema = useMemo(() => createLoginSchema(t), [t]);
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { identifier: defaultIdentifier, password: "" },
  });
  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (user) => {
      queryClient.setQueryData(CURRENT_ACTOR_QUERY_KEY, user);
      router.push("/");
    },
  });
  const apiError = mutation.error
    ? resolveApiErrorMessage(handleApiError(mutation.error, { shouldNotify: false }))
    : null;

  return (
    <form className="space-y-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Field data-invalid={Boolean(form.formState.errors.identifier)}>
        <FieldLabel htmlFor="login-identifier">{t("IDENTIFIER_LABEL")}</FieldLabel>
        <Input id="login-identifier" autoComplete="username" {...form.register("identifier")} />
        <FieldError>{form.formState.errors.identifier?.message}</FieldError>
      </Field>
      <Field data-invalid={Boolean(form.formState.errors.password)}>
        <FieldLabel htmlFor="login-password">{t("PASSWORD_LABEL")}</FieldLabel>
        <Input id="login-password" type="password" autoComplete="current-password"
          {...form.register("password")} />
        <FieldError>{form.formState.errors.password?.message}</FieldError>
      </Field>
      {apiError && <p className="text-sm text-destructive" role="alert">{apiError}</p>}
      <Button className="w-full" type="submit" disabled={mutation.isPending}>
        {t(mutation.isPending ? "MSG_LOGGING_IN" : "BTN_LOGIN")}
      </Button>
    </form>
  );
}
