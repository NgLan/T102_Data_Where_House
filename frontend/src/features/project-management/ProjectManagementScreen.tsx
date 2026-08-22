"use client";

import { CreateProjectDialog } from "./project-management-screen/project-creation/components/CreateProjectDialog";
import { ProjectList } from "./project-management-screen/ProjectList";
import { ProjectManagementHero } from "./project-management-screen/ProjectManagementHero";
import { ProjectToolbar } from "./project-management-screen/ProjectToolbar";
import { useProjectManagement } from "./hooks/use-project-management";

/** Public screen của feature Project Management. */
export function ProjectManagementScreen() {
  const state = useProjectManagement();
  return (
    <section className="mx-auto w-full max-w-7xl space-y-6 px-4 py-8">
      <ProjectManagementHero />
      <ProjectToolbar
        searchQuery={state.searchQuery}
        totalCount={state.projects.length}
        isRefreshing={state.isRefreshing}
        onSearchQueryChange={state.setSearchQuery}
        onRefreshProjects={state.refreshProjects}
        onCreateProject={() => state.setIsCreateDialogOpen(true)}
      />
      <ProjectList
        projects={state.filteredProjects}
        totalCount={state.projects.length}
        errorCode={state.errorCode}
        hasSearchQuery={Boolean(state.searchQuery.trim())}
        isInitialError={state.isInitialError}
        isInitialLoading={state.isInitialLoading}
        deletingProjectIds={state.deletingProjectIds}
        onRetry={state.refreshProjects}
        onClearSearch={() => state.setSearchQuery("")}
        onCreateProject={() => state.setIsCreateDialogOpen(true)}
        onDeleteProject={state.deleteProject}
      />
      <CreateProjectDialog
        isOpen={state.isCreateDialogOpen}
        onOpenChange={state.setIsCreateDialogOpen}
        onSubmit={state.createProject}
      />
    </section>
  );
}
