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
    <form className="space-y-3" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Field className="gap-1" data-invalid={Boolean(form.formState.errors.identifier)}>
        <FieldLabel htmlFor="login-identifier" className="text-xs">
          {t("IDENTIFIER_LABEL")} <span className="text-destructive font-medium ml-0.5">*</span>
        </FieldLabel>
        <Input
          id="login-identifier"
          className="h-9 px-3 text-sm"
          autoComplete="username"
          {...form.register("identifier")}
        />
        <FieldError className="text-xs">{form.formState.errors.identifier?.message}</FieldError>
      </Field>
      <Field className="gap-1" data-invalid={Boolean(form.formState.errors.password)}>
        <FieldLabel htmlFor="login-password" className="text-xs">
          {t("PASSWORD_LABEL")} <span className="text-destructive font-medium ml-0.5">*</span>
        </FieldLabel>
        <Input
          id="login-password"
          type="password"
          className="h-9 px-3 text-sm"
          autoComplete="current-password"
          {...form.register("password")}
        />
        <FieldError className="text-xs">{form.formState.errors.password?.message}</FieldError>
      </Field>
      {apiError && <p className="text-xs text-destructive" role="alert">{apiError}</p>}
      <Button
        className="w-full h-10 text-sm font-semibold transition-all shadow-sm hover:shadow-md active:scale-[0.99] mt-1"
        type="submit"
        disabled={mutation.isPending}
      >
        {t(mutation.isPending ? "MSG_LOGGING_IN" : "BTN_LOGIN")}
      </Button>
    </form>
  );
}
