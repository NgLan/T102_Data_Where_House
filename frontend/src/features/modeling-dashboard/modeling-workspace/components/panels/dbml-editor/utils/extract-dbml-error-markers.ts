import type { DataModelValidationIssueResponse } from "@/api";
import type { DbmlSyntaxError } from "../../../../model-document/dbml/types";

export interface DbmlEditorMarker {
  line: number;
  column: number;
  endColumn: number;
  message: string;
  severity: "error" | "warning";
}

interface ExtractMarkersOptions {
  code: string;
  syntaxErrors?: DbmlSyntaxError[];
  parseError?: string | null;
  validationIssues?: DataModelValidationIssueResponse[];
}

/** Tổng hợp vị trí các lỗi cú pháp và lỗi validation thành danh sách marker cho editor. */
export function extractDbmlErrorMarkers({
  code,
  syntaxErrors = [],
  parseError,
  validationIssues = [],
}: ExtractMarkersOptions): DbmlEditorMarker[] {
  const markers: DbmlEditorMarker[] = [];
  const lines = code.split("\n");

  // 1. Thêm syntax errors từ parser
  for (const err of syntaxErrors) {
    const lineIndex = Math.max(0, err.line - 1);
    const lineText = lines[lineIndex] ?? "";
    const col = Math.max(1, Math.min(err.column, lineText.length + 1));
    const endCol = Math.max(col + 1, Math.min(err.endColumn ?? (col + 1), lineText.length + 1));

    markers.push({
      line: err.line,
      column: col,
      endColumn: endCol,
      message: err.message ?? "MSG_DBML_SYNTAX_ERROR_DEFAULT",
      severity: "error",
    });
  }

  // Fallback nếu có parseError nhưng không có syntaxErrors cụ thể
  if (parseError && markers.length === 0 && lines.length > 0) {
    markers.push({
      line: lines.length,
      column: 1,
      endColumn: (lines[lines.length - 1]?.length ?? 0) + 1,
      message: parseError || "MSG_DBML_SYNTAX_ERROR_DEFAULT",
      severity: "error",
    });
  }

  // 2. Thêm semantic validation errors từ backend
  for (const issue of validationIssues) {
    if (issue.severity !== "ERROR") continue;
    const marker = findSemanticIssueMarker(lines, issue);
    if (marker) markers.push(marker);
  }

  return markers;
}

/** Tìm vị trí dòng của bảng hoặc cột bị lỗi validation semantic. */
function findSemanticIssueMarker(
  lines: string[],
  issue: DataModelValidationIssueResponse,
): DbmlEditorMarker | null {
  const tableRegex = new RegExp(
    `^[ \\t]*Table\\s+(?:[a-zA-Z0-9_"]+\\.)?["']?${escapeRegex(issue.table_name)}["']?\\b`,
    "i",
  );

  let inTargetTable = false;
  let targetTableLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (tableRegex.test(line)) {
      inTargetTable = true;
      targetTableLine = i + 1;
      if (!issue.column_name) {
        return {
          line: i + 1,
          column: 1,
          endColumn: line.length + 1,
          message: `${issue.title}: ${issue.description}`,
          severity: "error",
        };
      }
    }

    if (inTargetTable && issue.column_name) {
      const colRegex = new RegExp(`^[ \\t]*["']?${escapeRegex(issue.column_name)}["']?\\b`, "i");
      if (colRegex.test(line)) {
        return {
          line: i + 1,
          column: 1,
          endColumn: line.length + 1,
          message: `${issue.title}: ${issue.description}`,
          severity: "error",
        };
      }
      if (line.includes("}")) inTargetTable = false;
    }
  }

  if (targetTableLine > 0) {
    return {
      line: targetTableLine,
      column: 1,
      endColumn: (lines[targetTableLine - 1]?.length ?? 0) + 1,
      message: `${issue.title}: ${issue.description}`,
      severity: "error",
    };
  }

  return null;
}

function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
