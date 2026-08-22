/** Query keys ổn định cho Project Init. */
export const projectInitQueryKeys = {
  project: (projectId: string) => ["project-init", "project", projectId] as const,
  sources: (projectId: string) => ["project-init", "sources", projectId] as const,
  status: (projectId: string) => ["project-init", "status", projectId] as const,
  preview: (projectId: string, sourceId: string) =>
    ["project-init", "preview", projectId, sourceId] as const,
};
