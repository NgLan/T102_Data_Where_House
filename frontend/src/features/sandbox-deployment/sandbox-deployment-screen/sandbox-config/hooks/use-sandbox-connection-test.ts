"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import type { UseFormReturn } from "react-hook-form";
import { useAppNotification } from "@/common/notifications";
import {
  toSandboxConfigRequest,
  type SandboxConfigFormValues,
} from "../schemas/sandbox-config-form-schema";
import { testSandboxConnection } from "../services/sandbox-config-api";
import { applySandboxConfigApiErrors } from "../utils/apply-sandbox-config-api-errors";

export type ConnectionStatus = "idle" | "success" | "error";

/** Quản lý riêng mutation và trạng thái kiểm tra kết nối. */
export function useSandboxConnectionTest(
  projectId: string,
  form: UseFormReturn<SandboxConfigFormValues>,
  configFingerprint: string,
) {
  const { notifyError, notifySuccess } = useAppNotification();
  const [result, setResult] = useState<{
    fingerprint: string;
    status: ConnectionStatus;
    latencyMs: number | null;
  } | null>(null);
  const mutation = useMutation({
    mutationFn: (values: SandboxConfigFormValues) =>
      testSandboxConnection(projectId, parseValidValues(values)),
    onSuccess: (response, values) => {
      setResult({
        fingerprint: JSON.stringify(values),
        status: response.success ? "success" : "error",
        latencyMs: response.latency_ms ?? null,
      });
      if (response.success) notifySuccess("MSG_SANDBOX_CONNECTION_SUCCESS");
      else notifyError("SANDBOX_CONNECTION_FAILED");
    },
    onError: (error, values) => {
      setResult({
        fingerprint: JSON.stringify(values),
        status: "error",
        latencyMs: null,
      });
      const apiError = applySandboxConfigApiErrors(error, form);
      if (apiError?.kind === "validation") notifyError(apiError.errorCode);
    },
  });
  const isCurrent = result?.fingerprint === configFingerprint;
  return {
    mutation,
    status: isCurrent ? result.status : "idle",
    latencyMs: isCurrent ? result.latencyMs : null,
  };
}

function parseValidValues(
  values: SandboxConfigFormValues,
) {
  const request = toSandboxConfigRequest(values);
  if (!request) throw new Error("INVALID_SANDBOX_CONFIG");
  return request;
}
