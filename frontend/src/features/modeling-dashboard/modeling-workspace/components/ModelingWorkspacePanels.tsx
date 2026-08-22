import type { ReactNode } from "react";
import { useDefaultLayout } from "react-resizable-panels";
import type { DataModelValidationIssueResponse } from "@/api";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/common/components/ui/resizable";
import type { AgentDock } from "../../agent-sessions/hooks/use-agent-dock";
import { DBMLEditor } from "./panels/dbml-editor/components/DBMLEditor";
import { ERDCanvas } from "./panels/erd-canvas/components/ERDCanvas";
import type { useModelingWorkspace } from "../hooks/use-modeling-workspace";
import { DataModelInspector } from "./panels/model-inspector/DataModelInspector";

interface ModelingWorkspacePanelsProps {
  workspace: ReturnType<typeof useModelingWorkspace>;
  projectId: string;
  selectedTableName: string | null;
  validationIssues: DataModelValidationIssueResponse[];
  isInspectorOpen: boolean;
  agentDock: AgentDock;
  agentPanel: ReactNode;
  onClearSelection: () => void;
  proposalReview: ReactNode;
}

/** Bố trí các panel và giao toàn bộ resize cho component registry. */
export function ModelingWorkspacePanels(props: ModelingWorkspacePanelsProps) {
  const workspace = props.workspace;
  const layoutStorage =
    typeof window === "undefined" ? undefined : window.localStorage;
  const outerPanelIds = [
    "dbml",
    "erd",
    ...(props.isInspectorOpen && props.agentDock !== "inspector-bottom"
      ? ["inspector"]
      : []),
    ...(props.agentDock === "right" ? ["agent"] : []),
    ...(props.agentDock === "inspector-bottom" ? ["inspector-agent"] : []),
  ];
  const outerLayout = useDefaultLayout({
    id: `modeling-workspace:${props.projectId}`,
    panelIds: outerPanelIds,
    storage: layoutStorage,
    onlySaveAfterUserInteractions: true,
  });
  const inspectorLayout = useDefaultLayout({
    id: `modeling-inspector-agent:${props.projectId}`,
    panelIds: ["inspector", "agent"],
    storage: layoutStorage,
    onlySaveAfterUserInteractions: true,
  });
  const inspector = (
    <DataModelInspector
      document={workspace.document}
      validationErrors={workspace.validationErrors}
      selectedTableId={workspace.selectedTableId}
      selectedReferenceId={workspace.selectedReferenceId}
      mutate={workspace.mutate}
      onAddTable={workspace.addTable}
      onAddColumn={workspace.addColumn}
      onClearSelection={props.onClearSelection}
    />
  );
  return (
    <ResizablePanelGroup
      orientation="horizontal"
      className="min-h-0 flex-1"
      {...outerLayout}
    >
      <ResizablePanel id="dbml" defaultSize={25} minSize={18}>
        <DBMLEditor
          code={workspace.code}
          parseError={workspace.parseError}
          onChange={workspace.setCode}
          selectedTableName={props.selectedTableName}
          proposalReview={props.proposalReview}
        />
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel id="erd" defaultSize={45} minSize={25}>
        <ERDCanvas
          document={workspace.document}
          projectId={props.projectId}
          selectedTableId={workspace.selectedTableId}
          selectedReferenceId={workspace.selectedReferenceId}
          onSelectTable={workspace.selectTable}
          onSelectReference={workspace.selectReference}
          onCreateReference={workspace.addReference}
          validationIssues={props.validationIssues}
        />
      </ResizablePanel>
      {props.isInspectorOpen && props.agentDock !== "inspector-bottom" && (
        <DockPanel id="inspector">{inspector}</DockPanel>
      )}
      {props.agentDock === "right" && (
        <DockPanel id="agent">{props.agentPanel}</DockPanel>
      )}
      {props.agentDock === "inspector-bottom" && (
        <DockPanel id="inspector-agent">
          <ResizablePanelGroup orientation="vertical" {...inspectorLayout}>
            <ResizablePanel id="inspector" defaultSize={50} minSize={25}>
              {inspector}
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel id="agent" defaultSize={50} minSize={25}>
              {props.agentPanel}
            </ResizablePanel>
          </ResizablePanelGroup>
        </DockPanel>
      )}
    </ResizablePanelGroup>
  );
}

function DockPanel({ children, id }: { children: ReactNode; id: string }) {
  return (
    <>
      <ResizableHandle withHandle />
      <ResizablePanel id={id} defaultSize={30} minSize={22}>
        {children}
      </ResizablePanel>
    </>
  );
}
