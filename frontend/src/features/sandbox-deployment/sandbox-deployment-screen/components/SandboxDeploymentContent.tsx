import type { useDdlEditor } from "../ddl-editor/hooks/use-ddl-editor";
import type { useSandboxConfig } from "../sandbox-config/hooks/use-sandbox-config";
import type { useSandboxExecution } from "../sandbox-execution/hooks/use-sandbox-execution";
import { SandboxDeploymentLoadError } from "./SandboxDeploymentLoadError";
import { SandboxDeploymentSkeleton } from "./SandboxDeploymentSkeleton";
import { SandboxDeploymentWorkspace } from "./SandboxDeploymentWorkspace";

export interface SandboxDeploymentViewModels {
  config: ReturnType<typeof useSandboxConfig>;
  editor: ReturnType<typeof useDdlEditor>;
  execution: ReturnType<typeof useSandboxExecution>;
}

/** Chọn initial loading, load error hoặc workspace đã sẵn sàng. */
export function SandboxDeploymentContent(props: SandboxDeploymentViewModels) {
  if (props.config.isInitialLoading || props.editor.isInitialLoading) {
    return <SandboxDeploymentSkeleton />;
  }
  if (props.config.isInitialError || props.editor.isInitialError) {
    const errorCode = props.config.isInitialError
      ? props.config.errorCode
      : props.editor.errorCode;
    const handleRetry = () => {
      void Promise.all([props.config.retry(), props.editor.retry()]);
    };
    return <SandboxDeploymentLoadError errorCode={errorCode} onRetry={handleRetry} />;
  }
  return <SandboxDeploymentWorkspace {...props} />;
}
