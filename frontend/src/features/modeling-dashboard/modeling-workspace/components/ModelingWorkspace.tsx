"use client";

import "@xyflow/react/dist/style.css";
import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { Skeleton } from "@/common/components/ui/skeleton";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import { DBMLEditor } from "../dbml-editor/components/DBMLEditor";
import { ERDCanvas } from "../erd-canvas/components/ERDCanvas";
import { DataModelInspector } from "../model-inspector/components/DataModelInspector";
import { useModelingWorkspace } from "../hooks/use-modeling-workspace";
import { useWorkspaceShortcuts } from "../hooks/use-workspace-shortcuts";
import { ModelingWorkspaceHeader } from "./ModelingWorkspaceHeader";

interface ModelingWorkspaceProps {
  projectId: string;
}

/** Ghép DBML editor, React Flow canvas và inspector cho UC5.1.3.
 * @param props ID Project cần tải và lưu Data Model.
 * @returns Modeling workspace responsive dùng một canonical DbmlDocument draft.
 */
export function ModelingWorkspace({ projectId }: ModelingWorkspaceProps) {
  const { getErrorMessage } = useAppNotification();
  const [isInspectorOpen, setIsInspectorOpen] = useState(true);
  const workspace = useModelingWorkspace(projectId);
  const { canSave, isDirty, save, setSelectedTableId, setSelectedReferenceId } =
    workspace;
  const clearSelection = useCallback(() => {
    setSelectedTableId(null);
    setSelectedReferenceId(null);
  }, [setSelectedTableId, setSelectedReferenceId]);
  useWorkspaceShortcuts({
    canSave,
    isDirty,
    onClearSelection: clearSelection,
    onSave: save,
  });
  const selectedTable = workspace.document.tables.find(
    (item) => item.id === workspace.selectedTableId,
  );
  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden bg-white">
      <ModelingWorkspaceHeader
        projectId={projectId}
        canSave={workspace.canSave}
        errorMessage={workspace.errorCode ? getErrorMessage(workspace.errorCode) : null}
        hasProject={Boolean(projectId)}
        isDirty={workspace.isDirty}
        isInspectorOpen={isInspectorOpen}
        status={workspace.status}
        onReload={() => void workspace.load()}
        onSave={() => void workspace.save()}
        onToggleInspector={() => setIsInspectorOpen((current) => !current)}
      />
      {workspace.status === "loading" ? (
        <WorkspaceSkeleton />
      ) : (
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden lg:flex-row">
          <DBMLEditor
            code={workspace.code}
            parseError={workspace.parseError}
            onChange={workspace.setCode}
            selectedTableName={selectedTable?.name ?? null}
          />
          <ERDCanvas
            document={workspace.document}
            projectId={projectId}
            selectedTableId={workspace.selectedTableId}
            selectedReferenceId={workspace.selectedReferenceId}
            onSelectTable={workspace.selectTable}
            onSelectReference={workspace.selectReference}
            onCreateReference={workspace.addReference}
          />
          {isInspectorOpen && (
            <DataModelInspector
              document={workspace.document}
              validationErrors={workspace.validationErrors}
              selectedTableId={workspace.selectedTableId}
              selectedReferenceId={workspace.selectedReferenceId}
              mutate={workspace.mutate}
              onAddTable={workspace.addTable}
              onAddColumn={workspace.addColumn}
              onClearSelection={clearSelection}
            />
          )}
        </div>
      )}
    </section>
  );
}

function WorkspaceSkeleton() {
  const { t } = useTranslation("modeling-dashboard");
  return (
    <div
      className="grid min-h-0 flex-1 gap-3 p-3 lg:grid-cols-[300px_1fr_360px]"
      aria-label={t("TXT_LOADING")}
    >
      <Skeleton className="h-full" />
      <Skeleton className="h-full" />
      <Skeleton className="h-full" />
    </div>
  );
}
