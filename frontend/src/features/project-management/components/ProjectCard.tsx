"use client";

import { useState } from "react";
import Link from "next/link";
import { Calendar, FileSpreadsheet, Loader2, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectSummaryResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/confirmation-dialog";

interface ProjectCardProps {
  project: ProjectSummaryResponse;
  isDeleting: boolean;
  onDelete: (projectId: string) => Promise<void>;
}

/** Card semantic: link mở Project và button xóa là hai control độc lập. */
export function ProjectCard({ project, isDeleting, onDelete }: ProjectCardProps) {
  const { t, i18n } = useTranslation("project-management");
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const date = new Intl.DateTimeFormat(i18n.resolvedLanguage ?? i18n.language, {
    year: "numeric", month: "short", day: "numeric",
  }).format(new Date(project.updated_at));
  const handleDelete = async () => {
    await onDelete(project.id);
    setIsConfirmOpen(false);
  };
  return <article className="flex min-h-48 flex-col rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
    <div className="mb-3 flex items-center justify-between gap-2 text-xs text-muted-foreground">
      <span className="rounded-full bg-primary/10 px-2 py-1 font-semibold text-primary">{project.domain || t("CUSTOM_DOMAIN")}</span>
      <span className="flex items-center gap-1"><Calendar className="size-3" aria-hidden />{date}</span>
    </div>
    <Link href={`/projects/${project.id}`} className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      <h2 className="font-semibold text-foreground hover:text-primary">{project.name}</h2>
      <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{project.requirement}</p>
    </Link>
    <div className="mt-auto flex items-center justify-between border-t pt-3 text-xs text-muted-foreground">
      <span className="flex items-center gap-1"><FileSpreadsheet className="size-4" aria-hidden />{t("SOURCE_COUNT", { count: project.data_source_count })}</span>
      <Button variant="ghost" size="icon" onClick={() => setIsConfirmOpen(true)} disabled={isDeleting} aria-label={t("DELETE_PROJECT", { name: project.name })} title={t("DELETE")}>
        {isDeleting ? <Loader2 className="animate-spin" /> : <Trash2 />}
      </Button>
    </div>
    <ConfirmationDialog isOpen={isConfirmOpen} onOpenChange={setIsConfirmOpen} title={t("DELETE_TITLE")} content={t("DELETE_CONFIRM", { name: project.name })} actions={[
      { id: "cancel", label: t("CANCEL") },
      { id: "delete", label: t(isDeleting ? "DELETING" : "DELETE"), variant: "destructive", isDisabled: isDeleting, shouldClose: false, onSelect: () => { void handleDelete(); } },
    ]} />
  </article>;
}
