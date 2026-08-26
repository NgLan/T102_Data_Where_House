"use client";

import { Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useTranslation } from "react-i18next";
import { WorkflowStepNavigation } from "@/common/components/workflow/WorkflowStepNavigation";
import { useProjectStatusQuery } from "@/common/projects/project-queries";
import { parseWorkflowStep } from "@/common/routing/workflow-routing";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { ProjectSwitcher } from "./ProjectSwitcher";
import { ThemeSwitcher } from "./ThemeSwitcher";
import { UserMenu } from "./UserMenu";

interface AppHeaderProps {
  selectedProjectId?: string;
}

/** Header dùng chung cho mọi màn hình nghiệp vụ tích hợp stepper workflow.
 * @param props Project hiện hành để đồng bộ project switcher và workflow navigation.
 * @returns Header gồm logo, project, workflow stepper, locale, theme và actor menu.
 */
export function AppHeader({ selectedProjectId }: AppHeaderProps) {
  const { t } = useTranslation("common");
  return (
    <header className="z-40 shrink-0 border-b bg-background/90 backdrop-blur-md">
      <div className="flex min-h-14 items-center gap-2 px-3 sm:gap-4 sm:px-6">
        <Link
          href="/"
          className="flex cursor-pointer shrink-0 items-center gap-2.5 rounded-md font-bold
          text-foreground transition-colors hover:text-primary focus-visible:outline-none
          focus-visible:ring-2 focus-visible:ring-ring"
        >
          <span className="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-white p-0.5 shadow-xs border border-gray-200">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={44}
              height={44}
              className="size-full object-contain scale-110"
              priority
            />
          </span>
          <span className="hidden text-base font-bold sm:inline md:text-lg tracking-tight">
            {t("TXT_APP_NAME")}
          </span>
        </Link>
        <ProjectSwitcher selectedProjectId={selectedProjectId} />

        {selectedProjectId && (
          <div className="hidden lg:flex flex-1 justify-center max-w-xl mx-auto">
            <Suspense fallback={null}>
              <HeaderWorkflowNavigation projectId={selectedProjectId} />
            </Suspense>
          </div>
        )}

        <nav className="ml-auto flex shrink-0 items-center gap-1" aria-label={t("TXT_HEADER_ACTIONS")}>
          <LanguageSwitcher />
          <ThemeSwitcher />
          <UserMenu />
        </nav>
      </div>

      {selectedProjectId && (
        <div className="flex lg:hidden border-t px-3 py-1.5 justify-center bg-background/80">
          <Suspense fallback={null}>
            <HeaderWorkflowNavigation projectId={selectedProjectId} />
          </Suspense>
        </div>
      )}
    </header>
  );
}

function HeaderWorkflowNavigation({ projectId }: { projectId: string }) {
  const searchParams = useSearchParams();
  const currentStep = parseWorkflowStep(searchParams?.get("step") ?? undefined);
  const statusQuery = useProjectStatusQuery(projectId);
  return (
    <WorkflowStepNavigation
      projectId={projectId}
      currentStep={currentStep}
      hasDataModel={Boolean(statusQuery.data?.data_model_exists)}
    />
  );
}
