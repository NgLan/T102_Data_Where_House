import type { DdlDialect } from "./supported-ddl-dialects";

/** Query keys ổn định của feature Sandbox Deployment. */
export const sandboxDeploymentQueryKeys = {
  config: (projectId: string) =>
    ["sandbox-deployment", "config", projectId] as const,
  ddl: (projectId: string, dialect: DdlDialect) =>
    ["sandbox-deployment", "ddl", projectId, dialect] as const,
};
