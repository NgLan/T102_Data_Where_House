"use client";

import "@xyflow/react/dist/style.css";
import { useCallback, useState } from "react";
import { useAppNotification } from "@/common/notifications";
import { ValidationPanel } from "../validation/components/ValidationPanel";
import { useDraftValidation } from "../validation/hooks/use-draft-validation";
import { AgentSessionPanel } from "../agent-sessions/components/AgentSessionPanel";
import {
  useAgentDock,
  type AgentDock,
} from "../agent-sessions/hooks/use-agent-dock";
import { useAgentSessions } from "../agent-sessions/hooks/use-agent-sessions";
import { DraftRecoveryDialog } from "./components/draft-persistence/components/DraftRecoveryDialog";
import { useDraftAutosave } from "./components/draft-persistence/hooks/use-draft-autosave";
import { useDraftRecovery } from "./components/draft-persistence/hooks/use-draft-recovery";
import { useModelingWorkspace } from "./hooks/use-modeling-workspace";
import { useWorkspaceShortcuts } from "./hooks/use-workspace-shortcuts";
import { useProposalReview } from "./components/proposal-review/hooks/use-proposal-review";
import { ModelingWorkspaceHeader } from "./components/ModelingWorkspaceHeader";
import {
  EmptyModelNotice,
  GeneratingNotice,
  OutdatedModelNotice,
  WorkspaceSkeleton,
} from "./components/ModelingWorkspaceNotices";
import { ModelingWorkspacePanels } from "./components/ModelingWorkspacePanels";
import { ProposalReviewSection } from "./components/ProposalReviewSection";

/** Điều phối các capability cấp màn hình của Modeling workspace. */
export function ModelingWorkspace({ projectId }: { projectId: string }) {
  const { getErrorMessage } = useAppNotification();
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const workspace = useModelingWorkspace(projectId);
  const review = useProposalReview({ projectId, onApplied: workspace.applySnapshot });
  const agentDock = useAgentDock(projectId);
  const validation = useDraftValidation(
    projectId,
    workspace.code,
    workspace.parseError,
  );
  const canPersist = workspace.canSave && !validation.hasErrors;
  const ensureLatestModel = useCallback(async () => {
    if (!workspace.isDirty) return true;
    if (!canPersist) return false;
    return Boolean(await workspace.save());
  }, [canPersist, workspace]);
  const chat = useAgentSessions({
    projectId,
    ensureLatestModel,
    onProposal: review.showProposal,
    onInspectProposal: review.dismiss,
  });
  const saveDraft = workspace.save;
  const setSelectedTableId = workspace.setSelectedTableId;
  const setSelectedReferenceId = workspace.setSelectedReferenceId;
  const save = useCallback(async () => {
    await saveDraft();
  }, [saveDraft]);
  const clearSelection = useCallback(() => {
    setSelectedTableId(null);
    setSelectedReferenceId(null);
  }, [setSelectedReferenceId, setSelectedTableId]);
  const autosaveState = useDraftAutosave({
    draftKey: workspace.code,
    isDirty: workspace.isDirty,
    canSave: canPersist,
    onSave: workspace.save,
  });
  const recovery = useDraftRecovery({
    projectId,
    snapshot: workspace.snapshot,
    dbml: workspace.code,
    isDirty: workspace.isDirty,
    hasConflict: workspace.status === "conflict",
    onApplyServer: workspace.applySnapshot,
    onRestoreDbml: workspace.setCode,
  });
  useWorkspaceShortcuts({
    canSave: canPersist,
    isDirty: workspace.isDirty,
    onClearSelection: clearSelection,
    onSave: save,
  });

  const setAgentDock = (dock: AgentDock) => {
    agentDock.setDock(dock);
    if (dock === "inspector-bottom") setIsInspectorOpen(true);
  };
  const agentPanel = (
    <AgentSessionPanel
      projectId={projectId}
      sessions={chat.sessions}
      selectedSessionId={chat.selectedSessionId}
      events={chat.events}
      pendingClarification={chat.pendingClarification}
      draft={chat.draft}
      isSending={chat.isSending}
      pendingClientMessageId={chat.pendingClientMessageId}
      canSend={chat.canSend}
      errorCode={chat.errorCode}
      onSelectSession={chat.selectSession}
      onNewSession={() => void chat.createSession()}
      onDraftChange={chat.setDraft}
      onSend={() => void chat.send()}
      onAnswerClarification={(answer) => void chat.answerClarification(answer)}
      onDockChange={setAgentDock}
      onRenameSession={(title) => void chat.renameSession(title)}
    />
  );
  const selectedTableName =
    workspace.document.tables.find(
      (item) => item.id === workspace.selectedTableId,
    )?.name ?? null;
  const [highlightTarget, setHighlightTarget] = useState<{
    tableName: string;
    triggerAt: number;
  } | null>(null);

  const handleTableDoubleClick = useCallback((tableName: string) => {
    setHighlightTarget({ tableName, triggerAt: Date.now() });
  }, []);

  const selectTableByName = useCallback((tableName: string) => {
    const table = workspace.document.tables.find(
      (item) => item.name.toLowerCase() === tableName.toLowerCase(),
    );
    if (table) workspace.selectTable(table.id);
  }, [workspace]);
  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
      <ModelingWorkspaceHeader
        autosaveState={autosaveState}
        errorMessage={
          workspace.errorCode ? getErrorMessage(workspace.errorCode) : null
        }
        hasProject={Boolean(projectId)}
        isDirty={workspace.isDirty}
        isSaveBlocked={workspace.isDirty && !canPersist}
        lastSavedAt={workspace.snapshot?.updated_at ?? null}
        isInspectorOpen={isInspectorOpen}
        status={workspace.status}
        onToggleInspector={() => setIsInspectorOpen((current) => !current)}
        isAgentOpen={agentDock.dock !== "hidden"}
        onToggleAgent={() =>
          agentDock.setDock(agentDock.dock === "hidden" ? "right" : "hidden")
        }
      />
      {workspace.status === "empty" &&
        workspace.document.tables.length === 0 && (
          <EmptyModelNotice onGenerate={() => void workspace.generate()} />
        )}
      {workspace.snapshot?.is_outdated && workspace.status === "ready" && (
        <OutdatedModelNotice onUpdate={() => void workspace.generate()} />
      )}
      {workspace.status === "generating" && <GeneratingNotice />}
      {workspace.status === "loading" ? (
        <WorkspaceSkeleton />
      ) : (
        <ModelingWorkspacePanels
          workspace={workspace}
          projectId={projectId}
          selectedTableName={selectedTableName}
          highlightTarget={highlightTarget}
          onTableDoubleClick={handleTableDoubleClick}
          validationIssues={validation.issues}
          isInspectorOpen={isInspectorOpen}
          agentDock={agentDock.dock}
          agentPanel={agentPanel}
          onClearSelection={clearSelection}
          proposalReview={
            review.proposal ? <ProposalReviewSection review={review} /> : null
          }
        />
      )}
      <ValidationPanel {...validation} projectId={projectId} onSelectTable={selectTableByName} />
      <DraftRecoveryDialog
        candidate={recovery.candidate}
        onRestore={recovery.restore}
        onDiscard={recovery.discard}
      />
    </section>
  );
}
