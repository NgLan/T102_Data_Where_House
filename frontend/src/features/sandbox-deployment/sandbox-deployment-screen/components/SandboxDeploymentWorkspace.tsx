import { DdlEditor } from "../ddl-editor/components/DdlEditor";
import { SandboxControlPanel } from "./SandboxControlPanel";
import type { SandboxDeploymentViewModels } from "./SandboxDeploymentContent";

/** Ghép editor, config form và execution panel khi dữ liệu đã tải xong. */
export function SandboxDeploymentWorkspace(props: SandboxDeploymentViewModels) {
  return (
    <div className="flex flex-1 flex-col gap-4 lg:h-[calc(100vh-170px)] lg:max-h-[calc(100vh-170px)] lg:min-h-0 lg:flex-row">
      <DdlEditor
        ddlCode={props.editor.ddlCode}
        dialect={props.editor.dialect}
        isRefreshing={props.editor.isRefreshing}
        onCopyDdl={() => void props.editor.copy()}
        onDdlCodeChange={props.editor.setDdlCode}
        onDialectChange={props.editor.setDialect}
        onDownloadDocument={props.editor.downloadDocument}
        onDownloadSql={props.editor.downloadSql}
        onFormatDdl={props.editor.format}
      />
      <SandboxControlPanel {...props} />
    </div>
  );
}
