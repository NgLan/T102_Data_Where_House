import { SANDBOX_DB_TYPE } from "../../constants/supported-ddl-dialects";
import { SandboxConfigForm } from "../sandbox-config/components/SandboxConfigForm";
import { DeploySandboxAction } from "../sandbox-execution/components/DeploySandboxAction";
import { ExecutionLog } from "../sandbox-execution/components/ExecutionLog";
import type { SandboxTranslationKey } from "../sandbox-execution/types/execution-log-types";
import type { SandboxDeploymentViewModels } from "./SandboxDeploymentContent";

/** Ghép config form, deploy action và execution log trong cột điều khiển. */
export function SandboxControlPanel(props: SandboxDeploymentViewModels) {
  return (
    <aside className="flex min-h-0 flex-[3] flex-col gap-4 overflow-y-auto rounded-2xl border bg-card p-5 shadow-sm">
      <SandboxConfigForm
        form={props.config.form}
        isSaving={props.config.isSaving}
        isTestingConnection={props.config.isTestingConnection}
        connectionStatus={props.config.connectionStatus}
        connectionLatencyMs={props.config.connectionLatencyMs}
        onSave={props.config.save}
        onTestConnection={props.config.testConnection}
      />
      <DeploySandboxAction
        isDisabled={isDeployDisabled(props)}
        isExecuting={props.execution.isExecuting}
        isSchemaProtected={props.execution.isSchemaProtected}
        schemaName={props.execution.schemaName}
        shouldResetSchema={props.execution.shouldResetSchema}
        warningKey={deploymentWarning(props)}
        onExecute={props.execution.execute}
        onShouldResetSchemaChange={props.execution.setShouldResetSchema}
      />
      <ExecutionLog logs={props.execution.logs} />
    </aside>
  );
}

function isDeployDisabled(props: SandboxDeploymentViewModels): boolean {
  return props.execution.isExecuting || props.editor.isRefreshing ||
    !props.config.savedConfig || props.config.form.formState.isDirty ||
    !props.editor.ddlCode.trim() || props.editor.dialect !== SANDBOX_DB_TYPE;
}

function deploymentWarning(
  props: SandboxDeploymentViewModels,
): SandboxTranslationKey | undefined {
  if (!props.config.savedConfig) return "MSG_SAVE_CONFIG_BEFORE_DEPLOY";
  if (props.config.form.formState.isDirty) return "MSG_SAVE_CHANGES_BEFORE_DEPLOY";
  if (props.editor.dialect !== SANDBOX_DB_TYPE) return "MSG_POSTGRESQL_ONLY";
  if (!props.editor.ddlCode.trim()) return "MSG_DDL_REQUIRED";
  return undefined;
}
