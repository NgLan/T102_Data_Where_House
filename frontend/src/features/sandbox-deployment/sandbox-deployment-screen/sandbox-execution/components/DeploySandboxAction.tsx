import { Loader2, Play } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Checkbox } from "@/common/components/ui/checkbox";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";
import type { SandboxTranslationKey } from "../types/execution-log-types";

interface DeploySandboxActionProps {
  isDisabled: boolean;
  isExecuting: boolean;
  isSchemaProtected: boolean;
  schemaName: string;
  shouldResetSchema: boolean;
  warningKey?: SandboxTranslationKey;
  onExecute: () => void;
  onShouldResetSchemaChange: (value: boolean) => void;
}

/** Hiển thị reset policy và xác nhận destructive trước khi execute. */
export function DeploySandboxAction(props: DeploySandboxActionProps) {
  const shouldConfirm = props.shouldResetSchema && !props.isSchemaProtected;
  return (
    <section className="space-y-2 border-t pt-3">
      <SchemaResetControl {...props} />
      {shouldConfirm ? (
        <ResetConfirmation {...props} />
      ) : <ExecuteButton action={props} />}
      <DeploymentWarning warningKey={props.warningKey} />
    </section>
  );
}

function SchemaResetControl(props: DeploySandboxActionProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <label className="flex cursor-pointer items-start gap-2 text-xs text-muted-foreground">
      <Checkbox checked={props.shouldResetSchema} disabled={props.isSchemaProtected || props.isExecuting}
        onCheckedChange={(value) => props.onShouldResetSchemaChange(value === true)} />
      <span>{t("TXT_RESET_SCHEMA")}{props.isSchemaProtected && (
        <em className="ml-1 not-italic text-amber-700">{t("TXT_PUBLIC_SCHEMA_PROTECTED")}</em>
      )}</span>
    </label>
  );
}

function ExecuteButton({ action }: { action: DeploySandboxActionProps }) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <Button type="button" className="w-full" disabled={action.isDisabled}
      onClick={action.onExecute}>
      {action.isExecuting ? <Loader2 className="animate-spin" /> : <Play />}
      {action.isExecuting ? t("MSG_DEPLOYING") : t("BTN_DEPLOY")}
    </Button>
  );
}

function ResetConfirmation(props: DeploySandboxActionProps) {
  const { t } = useTranslation("sandbox-deployment");
  const { t: tCommon } = useTranslation("common");
  return (
    <ConfirmationDialog trigger={(
      <Button type="button" className="w-full" disabled={props.isDisabled}>
        {props.isExecuting ? <Loader2 className="animate-spin" /> : <Play />}
        {props.isExecuting ? t("MSG_DEPLOYING") : t("BTN_DEPLOY")}
      </Button>
    )}
      title={t("TXT_RESET_CONFIRM_TITLE")}
      content={t("TXT_RESET_CONFIRM_DESCRIPTION", { schemaName: props.schemaName })}
      actions={[
        { id: "cancel", label: tCommon("BTN_CANCEL"), variant: "outline" },
        { id: "execute", label: t("BTN_RESET_AND_EXECUTE"), onSelect: props.onExecute },
      ]} />
  );
}

function DeploymentWarning({ warningKey }: { warningKey?: SandboxTranslationKey }) {
  const { t } = useTranslation("sandbox-deployment");
  return warningKey ? (
    <p className="text-xs text-amber-700" role="status">{t(warningKey)}</p>
  ) : null;
}
