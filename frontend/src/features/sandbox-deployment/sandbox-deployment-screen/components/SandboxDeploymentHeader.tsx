import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { createWorkflowHref } from "@/common/routing/workflow-routing";

/** Hiển thị tiêu đề feature và điều hướng quay lại Modeling. */
export function SandboxDeploymentHeader({ projectId }: { projectId: string }) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <header className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-card/80 px-5 py-3 shadow-xs backdrop-blur-md">
      <div>
        <h1 className="text-lg font-extrabold tracking-tight">{t("TXT_SCREEN_TITLE")}</h1>
        <p className="text-xs text-muted-foreground">{t("TXT_SCREEN_SUBTITLE")}</p>
      </div>
      <Button asChild variant="outline">
        <Link href={createWorkflowHref("modeling", projectId)}>
          <ArrowLeft aria-hidden="true" />
          {t("BTN_BACK_TO_MODELING")}
        </Link>
      </Button>
    </header>
  );
}
