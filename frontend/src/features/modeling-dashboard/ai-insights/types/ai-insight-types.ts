/** Mức độ nghiêm trọng của một insight trình bày trên UI. */
export type AIInsightSeverity = "info" | "error" | "warn";

/** View model local của một AI insight. */
export interface AIInsight {
  id: string;
  tableName: string;
  severity: AIInsightSeverity;
  title: string;
  description: string;
}
