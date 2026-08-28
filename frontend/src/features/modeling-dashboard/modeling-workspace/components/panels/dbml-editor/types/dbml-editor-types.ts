import type { ReactNode } from "react";
import type { DataModelValidationIssueResponse } from "@/api";
import type { DbmlSyntaxError } from "../../../../model-document/dbml/types";

export interface DbmlHighlightTarget {
  tableName: string;
  triggerAt: number;
}

export interface DBMLEditorProps {
  code: string;
  parseError: string | null;
  syntaxErrors?: DbmlSyntaxError[];
  validationIssues?: DataModelValidationIssueResponse[];
  onChange: (value: string) => void;
  selectedTableName?: string | null;
  highlightTarget?: DbmlHighlightTarget | null;
  proposalReview?: ReactNode;
}
