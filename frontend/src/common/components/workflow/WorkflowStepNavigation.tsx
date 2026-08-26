"use client";

import Link from "next/link";
import { useTranslation } from "react-i18next";
import { cn } from "@/common/lib/utils";
import { createWorkflowHref, type WorkflowStep } from "@/common/routing/workflow-routing";

interface WorkflowStepNavigationProps {
  projectId: string;
  currentStep: WorkflowStep;
  hasDataModel: boolean;
  disabled?: boolean;
  className?: string;
}

const STEPS: readonly WorkflowStep[] = ["project-init", "modeling", "sandbox"];

/** Thanh điều hướng bước workflow tích hợp trên AppHeader.
 * @param props Thuộc tính project, bước hiện tại và trạng thái kích hoạt.
 * @returns Khối navigation 3 bước phản hồi trạng thái URL.
 */
export function WorkflowStepNavigation(props: WorkflowStepNavigationProps) {
  const { t } = useTranslation("common");
  return (
    <nav
      aria-label={t("TXT_WORKFLOW_NAVIGATION")}
      className={cn(
        "inline-flex items-center gap-1 rounded-xl bg-muted/60 p-1 border shadow-2xs",
        props.className,
      )}
    >
      {STEPS.map((step, index) => {
        const isEnabled = !props.disabled && (step === "project-init" || props.hasDataModel);
        const isActive = step === props.currentStep;
        const label = t(`TXT_WORKFLOW_STEP_${step.replace("-", "_").toUpperCase()}`);
        const content = (
          <span
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs sm:text-sm font-medium transition-all",
              isActive && "bg-primary text-primary-foreground font-semibold shadow-xs",
              !isEnabled && "cursor-not-allowed text-muted-foreground/60 opacity-60",
              isEnabled && !isActive && "cursor-pointer text-muted-foreground hover:bg-background hover:text-foreground",
            )}
          >
            <span
              className={cn(
                "flex size-4 sm:size-4.5 items-center justify-center rounded-full text-[10px] sm:text-xs font-bold",
                isActive ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground",
              )}
            >
              {index + 1}
            </span>
            <span className="truncate">{label}</span>
          </span>
        );
        return isEnabled ? (
          <Link key={step} href={createWorkflowHref(step, props.projectId)}>
            {content}
          </Link>
        ) : (
          <span key={step} aria-disabled="true">
            {content}
          </span>
        );
      })}
    </nav>
  );
}
