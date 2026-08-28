import type { ReactNode } from "react";

export interface DbmlHighlightTarget {
  tableName: string;
  triggerAt: number;
}

export interface DBMLEditorProps {
  code: string;
  parseError: string | null;
  onChange: (value: string) => void;
  selectedTableName?: string | null;
  highlightTarget?: DbmlHighlightTarget | null;
  proposalReview?: ReactNode;
}
