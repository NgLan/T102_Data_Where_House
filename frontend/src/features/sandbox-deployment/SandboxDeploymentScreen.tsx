"use client";

import { MainLayout } from "@/common/components/layout/MainLayout";
import { SandboxDeploymentContent } from "./sandbox-deployment-screen/components/SandboxDeploymentContent";
import { SandboxDeploymentHeader } from "./sandbox-deployment-screen/components/SandboxDeploymentHeader";
import { useDdlEditor } from "./sandbox-deployment-screen/ddl-editor/hooks/use-ddl-editor";
import { useSandboxConfig } from "./sandbox-deployment-screen/sandbox-config/hooks/use-sandbox-config";
import { useSandboxExecution } from "./sandbox-deployment-screen/sandbox-execution/hooks/use-sandbox-execution";

interface SandboxDeploymentScreenProps {
  projectId: string;
}

/** Điều phối ba capability của màn hình Sandbox Deployment. */
export function SandboxDeploymentScreen({ projectId }: SandboxDeploymentScreenProps) {
  const config = useSandboxConfig(projectId);
  const editor = useDdlEditor(projectId, config.form.watch("databaseName"));
  const execution = useSandboxExecution({
    projectId,
    ddlCode: editor.ddlCode,
    dialect: editor.dialect,
    savedConfig: config.savedConfig,
  });
  return (
    <MainLayout selectedProjectId={projectId}>
      <div className="flex w-full flex-1 flex-col space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <SandboxDeploymentHeader projectId={projectId} />
        <SandboxDeploymentContent config={config} editor={editor} execution={execution} />
      </div>
    </MainLayout>
  );
}
