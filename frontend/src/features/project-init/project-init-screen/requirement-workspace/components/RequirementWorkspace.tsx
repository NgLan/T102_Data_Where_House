"use client";

import type { UseFormReturn } from "react-hook-form";
import { RefreshCw } from "lucide-react";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Skeleton } from "@/common/components/ui/skeleton";
import type { ProjectDetailsValues } from "../../project-details/schemas/project-details-schema";
import { RawRequirementField } from "../../project-details/components/RawRequirementField";
import { StructuredRequirementsTable } from "../../project-details/components/StructuredRequirementsTable";
import { useRequirementClarification } from "../hooks/use-requirement-clarification";
import { useRequirementFiles } from "../hooks/use-requirement-files";
import { RequirementChat } from "./RequirementChat";
import { RequirementDocuments } from "./RequirementDocuments";

interface RequirementWorkspaceProps {
  projectId: string;
  canEdit: boolean;
  form: UseFormReturn<ProjectDetailsValues>;
  isRawDirty: boolean;
  isWorkflowRunning: boolean;
  clarification: ReturnType<typeof useRequirementClarification>;
  isChatOpen: boolean;
  onChatOpenChange: (isOpen: boolean) => void;
  onSaveDraft: () => Promise<void>;
  onContinueAnalysis: () => Promise<void>;
}

/** Workspace tách document, raw draft, structured output và clarification chat. */
export function RequirementWorkspace(props: RequirementWorkspaceProps) {
  const { t } = useTranslation("project-init");
  const workspaceRef = useRef<HTMLElement>(null);
  const files = useRequirementFiles(props.projectId);
  const clarification = props.clarification;
  const state = clarification.stateQuery.data;
  const isBusy =
    files.isMutating || clarification.isProcessing || props.isWorkflowRunning;

  useEffect(() => {
    if (props.isChatOpen) {
      workspaceRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [props.isChatOpen]);

  return (
    <section
      ref={workspaceRef}
      className="space-y-4 rounded-xl border bg-background p-5"
    >
      <header>
        <h2 className="font-semibold">
          {t("TXT_REQUIREMENT_WORKSPACE_TITLE")}
        </h2>
        <p className="text-sm text-muted-foreground">
          {t("TXT_REQUIREMENT_WORKSPACE_SUBTITLE")}
        </p>
      </header>
      <RequirementDocuments
        items={files.files}
        disabled={!props.canEdit || isBusy}
        isLoading={files.filesQuery.isLoading}
        hasError={files.filesQuery.isError}
        onUpload={(items) => void files.upload(items)}
        onDelete={(id) => void files.deleteFile(id)}
        onRetry={() => void files.filesQuery.refetch()}
      />
      {state?.is_outdated && (
        <p className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">
          {t("TXT_REQUIREMENT_OUTDATED")}
        </p>
      )}
      <div
        className={
          props.isChatOpen
            ? "grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_24rem]"
            : "grid items-start gap-4"
        }
      >
        <div className="grid items-stretch gap-4 xl:grid-cols-2">
          <RawRequirementField
            control={props.form.control}
            disabled={!props.canEdit || isBusy}
            error={
              props.form.formState.errors.requirement
                ? "MSG_PROJECT_REQUIREMENT_MIN"
                : undefined
            }
            isDirty={props.isRawDirty}
            onSaveDraft={() => void props.onSaveDraft()}
          />
          <div className="relative">
            {clarification.stateQuery.isLoading ? (
              <Skeleton className="h-[58vh] min-h-112 w-full" />
            ) : clarification.stateQuery.isError ? (
              <div className="flex h-[58vh] min-h-112 flex-col items-center justify-center gap-3 rounded-lg border text-center">
                <p className="text-sm text-muted-foreground">
                  {t("TXT_REQUIREMENT_CLARIFICATION_ERROR")}
                </p>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void clarification.stateQuery.refetch()}
                >
                  <RefreshCw />
                  {t("BTN_RETRY")}
                </Button>
              </div>
            ) : (
              <StructuredRequirementsTable
                items={state?.requirements ?? []}
                canDelete={props.canEdit}
                isDeleting={clarification.deleteMutation.isPending}
                onDelete={clarification.deleteRequirement}
                newIds={clarification.turnDiff?.newIds}
                changedIds={clarification.turnDiff?.changedIds}
                deletedTitles={clarification.turnDiff?.deletedTitles}
                onOpenChat={() => props.onChatOpenChange(true)}
                isChatOpen={props.isChatOpen}
                hasPendingQuestion={Boolean(
                  state?.pending_question ||
                  state?.continuation_state === "AWAITING_DECISION",
                )}
              />
            )}
          </div>
        </div>
        <RequirementChat
          isOpen={props.isChatOpen}
          onOpenChange={props.onChatOpenChange}
          status={
            clarification.isProcessing
              ? "PROCESSING"
              : (state?.status ?? "IDLE")
          }
          continuationState={state?.continuation_state ?? "NOT_REQUIRED"}
          events={clarification.eventsQuery.data ?? []}
          pending={state?.pending_question ?? null}
          canAnswer={props.canEdit}
          isSending={clarification.isProcessing || props.isWorkflowRunning}
          hasError={
            clarification.answerMutation.isError ||
            clarification.messageMutation.isError ||
            clarification.continuationMutation.isError
          }
          onAnswer={clarification.answer}
          onMessage={clarification.sendMessage}
          onContinueEditing={() =>
            clarification.chooseContinuation("CONTINUE_EDITING")
          }
          onContinueAnalysis={props.onContinueAnalysis}
        />
      </div>
    </section>
  );
}
