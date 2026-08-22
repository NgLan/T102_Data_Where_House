import { Database, Loader2, PlugZap, Save } from "lucide-react";
import type { UseFormReturn } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import type { ConnectionStatus } from "../hooks/use-sandbox-connection-test";
import type { SandboxConfigFormValues } from "../schemas/sandbox-config-form-schema";
import { SandboxConfigFields } from "./SandboxConfigFields";
import { SandboxConnectionStatus } from "./SandboxConnectionStatus";

interface SandboxConfigFormProps {
  connectionLatencyMs: number | null;
  connectionStatus: ConnectionStatus;
  form: UseFormReturn<SandboxConfigFormValues>;
  isSaving: boolean;
  isTestingConnection: boolean;
  onSave: () => void;
  onTestConnection: () => void;
}

/** Hiển thị và validate cấu hình PostgreSQL Sandbox. */
export function SandboxConfigForm(props: SandboxConfigFormProps) {
  const { t } = useTranslation("sandbox-deployment");
  const isBusy = props.isSaving || props.isTestingConnection;
  return (
    <form className="space-y-4" onSubmit={props.onSave} noValidate>
      <SandboxConfigHeader {...props} />
      <SandboxConfigFields disabled={isBusy} form={props.form} />
      {props.form.formState.isDirty && (
        <p className="text-xs text-amber-700" role="status">
          {t("MSG_UNSAVED_CONFIG")}
        </p>
      )}
      <SandboxConfigActions {...props} />
    </form>
  );
}

function SandboxConfigHeader(props: SandboxConfigFormProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <header className="space-y-1 border-b pb-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 text-sm font-bold">
          <Database className="size-4 text-blue-600" aria-hidden="true" />
          {t("TXT_SANDBOX_TITLE")}
        </h2>
        <SandboxConnectionStatus latencyMs={props.connectionLatencyMs} status={props.connectionStatus} />
      </div>
      <p className="text-xs text-muted-foreground">{t("TXT_SANDBOX_DESCRIPTION")}</p>
    </header>
  );
}

function SandboxConfigActions(props: SandboxConfigFormProps) {
  const { t } = useTranslation("sandbox-deployment");
  const isBusy = props.isSaving || props.isTestingConnection;
  return (
    <div className="flex flex-wrap gap-2 border-t pt-3">
      <Button type="button" size="sm" variant="outline" className="flex-1" disabled={isBusy} onClick={props.onTestConnection}>
        {props.isTestingConnection ? <Loader2 className="animate-spin" /> : <PlugZap />}
        {props.isTestingConnection ? t("MSG_TESTING_CONNECTION") : t("BTN_TEST_CONNECTION")}
      </Button>
      <Button type="submit" size="sm" className="flex-1" disabled={isBusy || !props.form.formState.isDirty}>
        {props.isSaving ? <Loader2 className="animate-spin" /> : <Save />}
        {props.isSaving ? t("MSG_SAVING_CONFIG") : t("BTN_SAVE_CONFIG")}
      </Button>
    </div>
  );
}
