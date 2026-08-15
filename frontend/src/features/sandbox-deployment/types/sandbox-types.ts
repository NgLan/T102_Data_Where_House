/**
 * Types & Interfaces cho Feature Sandbox Deployment & DDL Editor
 */

import type { TerminalLogEntryDto } from '@/api/model/sandbox.dto';

export interface SandboxConfigState {
  hostConnection: string;
  targetDatabase: string;
}

export interface SandboxDeploymentState {
  ddlScript: string;
  logs: TerminalLogEntryDto[];
  isDeploying: boolean;
}
