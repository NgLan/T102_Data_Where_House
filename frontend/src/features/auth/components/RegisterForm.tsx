"use client";

import { useMemo } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm, type UseFormRegisterReturn } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { handleApiError, resolveApiErrorMessage } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Field, FieldError, FieldLabel } from "@/common/components/ui/field";
import { Input } from "@/common/components/ui/input";
import { toast } from "sonner";
import { createRegisterSchema, type RegisterFormValues } from "../schemas/auth-schemas";
import { registerUser } from "../services/auth-api";

interface RegisterFormProps {
  onRegisterSuccess?: (registeredUsername: string) => void;
}

export function RegisterForm({ onRegisterSuccess }: RegisterFormProps) {
  const { t } = useTranslation("auth");
  const schema = useMemo(() => createRegisterSchema(t), [t]);
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { username: "", email: "", full_name: "", password: "" },
  });
  const mutation = useMutation({
    mutationFn: registerUser,
    onSuccess: (_, variables) => {
      toast.success(t("MSG_REGISTER_SUCCESS"));
      form.reset();
      onRegisterSuccess?.(variables.username);
    },
  });
  const apiError = mutation.error
    ? resolveApiErrorMessage(handleApiError(mutation.error, { shouldNotify: false }))
    : null;

  return (
    <form className="space-y-3" onSubmit={form.handleSubmit((values) => mutation.mutate({
      ...values, full_name: values.full_name || undefined,
    }))}>
      <AuthField id="register-username" label={t("USERNAME_LABEL")}
        error={form.formState.errors.username?.message} autoComplete="username"
        registration={form.register("username")} />
      <AuthField id="register-email" label={t("EMAIL_LABEL")}
        error={form.formState.errors.email?.message} autoComplete="email" type="email"
        registration={form.register("email")} />
      <AuthField id="register-full-name" label={t("FULL_NAME_LABEL")}
        error={form.formState.errors.full_name?.message} autoComplete="name"
        registration={form.register("full_name")} />
      <AuthField id="register-password" label={t("PASSWORD_LABEL")}
        error={form.formState.errors.password?.message} autoComplete="new-password" type="password"
        registration={form.register("password")} />
      {apiError && <p className="text-sm text-destructive" role="alert">{apiError}</p>}
      <Button className="w-full" type="submit" disabled={mutation.isPending}>
        {t(mutation.isPending ? "MSG_REGISTERING" : "BTN_REGISTER")}
      </Button>
    </form>
  );
}

function AuthField(props: {
  id: string;
  label: string;
  error?: string;
  type?: string;
  autoComplete: string;
  registration: UseFormRegisterReturn;
}) {
  return (
    <Field data-invalid={Boolean(props.error)}>
      <FieldLabel htmlFor={props.id}>{props.label}</FieldLabel>
      <Input id={props.id} type={props.type} autoComplete={props.autoComplete} {...props.registration} />
      <FieldError>{props.error}</FieldError>
    </Field>
  );
}
