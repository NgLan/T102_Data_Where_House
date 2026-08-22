"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm, useWatch, type UseFormReturn } from "react-hook-form";
import { isApiError, type SandboxConfigRequest } from "@/api";
import { useAppNotification } from "@/common/notifications";
import { sandboxDeploymentQueryKeys } from "../../../constants/sandbox-deployment-query-keys";
import {
  DEFAULT_SANDBOX_CONFIG,
  sandboxConfigFormSchema,
  toSandboxConfigFormValues,
  toSandboxConfigRequest,
  type SandboxConfigFormValues,
} from "../schemas/sandbox-config-form-schema";
import { getSandboxConfig, saveSandboxConfig } from "../services/sandbox-config-api";
import { applySandboxConfigApiErrors } from "../utils/apply-sandbox-config-api-errors";
import { useSandboxConnectionTest } from "./use-sandbox-connection-test";

/** Quản lý form, persistence và connection test của Sandbox config. */
export function useSandboxConfig(projectId: string) {
  const query = useQuery({
    queryKey: sandboxDeploymentQueryKeys.config(projectId),
    queryFn: () => getSandboxConfig(projectId),
  });
  const form = useSyncedSandboxForm(query.data, query.isSuccess);
  const fingerprint = JSON.stringify(useWatch({ control: form.control }));
  const saveMutation = useSandboxConfigSave(projectId, form);
  const connectionTest = useSandboxConnectionTest(projectId, form, fingerprint);
  return {
    form,
    savedConfig: query.data ?? null,
    errorCode: isApiError(query.error) ? query.error.errorCode : "UNKNOWN_ERROR",
    isInitialError: query.isError,
    isInitialLoading: query.isPending,
    isSaving: saveMutation.isPending,
    isTestingConnection: connectionTest.mutation.isPending,
    connectionStatus: connectionTest.status,
    connectionLatencyMs: connectionTest.latencyMs,
    save: form.handleSubmit((values) => saveMutation.mutate(values)),
    testConnection: form.handleSubmit((values) =>
      connectionTest.mutation.mutate(values),
    ),
    retry: query.refetch,
  };
}

function useSyncedSandboxForm(
  config: Awaited<ReturnType<typeof getSandboxConfig>> | undefined,
  isFetched: boolean,
) {
  const form = useForm<SandboxConfigFormValues>({
    defaultValues: DEFAULT_SANDBOX_CONFIG,
    resolver: zodResolver(sandboxConfigFormSchema),
  });
  useEffect(() => {
    if (isFetched && !form.formState.isDirty) {
      form.reset(toSandboxConfigFormValues(config ?? null));
    }
  }, [config, form, form.formState.isDirty, isFetched]);
  return form;
}

function useSandboxConfigSave(
  projectId: string,
  form: UseFormReturn<SandboxConfigFormValues>,
) {
  const queryClient = useQueryClient();
  const { notifyError, notifySuccess } = useAppNotification();
  return useMutation({
    mutationFn: (values: SandboxConfigFormValues) =>
      saveSandboxConfig(projectId, requireConfigRequest(values)),
    onSuccess: (config) => {
      queryClient.setQueryData(
        sandboxDeploymentQueryKeys.config(projectId),
        config,
      );
      form.reset(toSandboxConfigFormValues(config));
      notifySuccess("MSG_SANDBOX_CONFIG_SAVED");
    },
    onError: (error) => {
      const apiError = applySandboxConfigApiErrors(error, form);
      if (apiError?.kind === "validation") notifyError(apiError.errorCode);
    },
  });
}

function requireConfigRequest(
  values: SandboxConfigFormValues,
): SandboxConfigRequest {
  const request = toSandboxConfigRequest(values);
  if (!request) throw new Error("INVALID_SANDBOX_CONFIG");
  return request;
}
