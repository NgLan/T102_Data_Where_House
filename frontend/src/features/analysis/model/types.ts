export type TableRole = "Fact" | "Dimension";

export type WarningSeverity = "critical" | "warning" | "info";

export interface KeyDecision {
  column: string;
  kind: "Primary key" | "Foreign key";
  rationale: string;
  reference?: string;
}

export interface AnalysisWarning {
  code: string;
  severity: WarningSeverity;
  title: string;
  message: string;
  recommendation: string;
}

export interface TableAnalysis {
  id: string;
  name: string;
  role: TableRole;
  grain: string;
  grainRationale: string;
  keyDecisions: KeyDecision[];
  warnings: AnalysisWarning[];
}

export interface ModelAnalysis {
  modelName: string;
  version: number;
  generatedAt: string;
  qualityScore: number;
  summary: string;
  tables: TableAnalysis[];
}
