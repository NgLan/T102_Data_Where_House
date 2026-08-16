"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { MainLayout } from "@/common/components/layout/MainLayout";
import { createWorkflowHref } from "@/common/routing/workflow-routing";
import { DdlCodeEditor } from "./components/DdlCodeEditor";
import { SandboxConfigCard } from "./components/SandboxConfigCard";
import { useSandboxDeploy } from "./hooks/use-sandbox-deploy";

interface SandboxDeploymentScreenProps {
  projectId: string;
}

/** Điều phối màn hình chỉnh DDL và triển khai sandbox.
 * @param props ID Project lấy trực tiếp từ route workspace.
 * @returns Feature screen gồm editor, cấu hình và terminal thực thi.
 */
export function SandboxDeploymentScreen({ projectId }: SandboxDeploymentScreenProps) {
  const { t } = useTranslation("sandbox-deployment");
  const sandbox = useSandboxDeploy();
  return (
    <MainLayout>
      <div className="flex w-full flex-1 flex-col space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <header className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/80 bg-white/80 px-5 py-3 shadow-xs backdrop-blur-md">
          <div>
            <h1 className="text-lg font-extrabold tracking-tight text-slate-900">
              {t("TXT_SCREEN_TITLE")}
            </h1>
            <p className="text-xs text-slate-500">{t("TXT_SCREEN_SUBTITLE")}</p>
          </div>
          <Button asChild variant="outline">
            <Link href={createWorkflowHref("modeling", projectId)}>
              <ArrowLeft />
              {t("BTN_BACK_TO_MODELING")}
            </Link>
          </Button>
        </header>
        <div className="flex flex-1 flex-col gap-4 lg:min-h-[calc(100vh-170px)] lg:flex-row">
          <DdlCodeEditor
            ddlCode={sandbox.ddlCode}
            onChange={sandbox.setDdlCode}
            onFormat={sandbox.handleFormatDdl}
            onCopy={sandbox.handleCopyDdl}
            onDownloadDoc={sandbox.handleDownloadDoc}
            onDownloadSql={sandbox.handleDownloadDdl}
          />
          <SandboxConfigCard
            host={sandbox.hostConnection}
            onHostChange={sandbox.setHostConnection}
            database={sandbox.databaseSchema}
            onDatabaseChange={sandbox.setDatabaseSchema}
            logs={sandbox.logs}
            isDeploying={sandbox.isDeploying}
            onDeploy={sandbox.handleDeploySandbox}
            onGenerateTestData={sandbox.handleGenerateTestData}
          />
        </div>
      </div>
    </MainLayout>
  );
}
