/** Query keys ổn định cho Project Init. */
export const projectInitQueryKeys = {
  project: (projectId: string) => ["project-init", "project", projectId] as const,
  sources: (projectId: string) => ["project-init", "sources", projectId] as const,
  status: (projectId: string) => ["project-init", "status", projectId] as const,
  requirementFiles: (projectId: string) =>
    ["project-init", "requirement-files", projectId] as const,
  clarification: (projectId: string) =>
    ["project-init", "requirement-clarification", projectId] as const,
  clarificationEvents: (sessionId: string | null) =>
    ["project-init", "requirement-clarification-events", sessionId] as const,
  preview: (projectId: string, sourceId: string, tableName?: string) =>
    ["project-init", "preview", projectId, sourceId, tableName ?? null] as const,
};
