import sandboxVi from "@/common/i18n/locales/vi/sandbox-deployment.json";

export type SandboxTranslationKey = keyof typeof sandboxVi;
export type ExecutionLogType = "info" | "success" | "error";

interface ExecutionLogBase {
  id: string;
  timestamp: string;
  type: ExecutionLogType;
}

export interface TranslatedExecutionLogEntry extends ExecutionLogBase {
  translationKey: SandboxTranslationKey;
  params?: Record<string, string | number>;
  errorCode?: never;
}

export interface ErrorCodeExecutionLogEntry extends ExecutionLogBase {
  errorCode: string;
  translationKey?: never;
  params?: never;
}

export type ExecutionLogEntry =
  | TranslatedExecutionLogEntry
  | ErrorCodeExecutionLogEntry;
