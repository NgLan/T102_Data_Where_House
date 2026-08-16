"use client";

import { useTranslation } from "react-i18next";
import { CreateProjectDialog } from "./components/CreateProjectDialog";
import { ProjectListState } from "./components/ProjectListState";
import { ProjectToolbar } from "./components/ProjectToolbar";
import { useProjectManagement } from "./hooks/use-project-management";

/** Public screen của feature Project Management. */
export function ProjectManagementScreen() {
  const { t } = useTranslation("project-management");
  const state = useProjectManagement();
  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-4 py-8">
      <header className="rounded-2xl bg-gradient-to-br from-slate-950 to-indigo-950 p-8 text-white">
        <p className="text-xs font-semibold uppercase tracking-wider text-blue-300">
          {t("EYEBROW")}
        </p>
        <h1 className="mt-2 text-2xl font-bold">{t("TITLE")}</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-300">{t("SUBTITLE")}</p>
      </header>
      <ProjectToolbar
        query={state.searchQuery}
        totalCount={state.totalCount}
        isRefreshing={state.status === "refreshing"}
        onQueryChange={state.setSearchQuery}
        onRefresh={state.refreshProjects}
        onCreate={() => state.setIsCreateOpen(true)}
      />
      <ProjectListState
        projects={state.projects}
        totalCount={state.totalCount}
        status={state.status}
        errorCode={state.errorCode}
        hasSearch={Boolean(state.searchQuery.trim())}
        deletingIds={state.deletingIds}
        onRetry={state.retryProjects}
        onClearSearch={() => state.setSearchQuery("")}
        onCreate={() => state.setIsCreateOpen(true)}
        onDelete={state.deleteProject}
      />
      <CreateProjectDialog
        isOpen={state.isCreateOpen}
        onOpenChange={state.setIsCreateOpen}
        onSubmit={state.createProject}
      />
    </main>
  );
}
