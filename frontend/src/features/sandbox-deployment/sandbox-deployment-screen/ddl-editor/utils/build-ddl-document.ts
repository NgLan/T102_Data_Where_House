interface BuildDdlDocumentInput {
  title: string;
  databaseName: string;
  ddlCode: string;
}

/** Tạo tài liệu Markdown chứa DDL đang hiển thị trong editor. */
export function buildDdlDocument(input: BuildDdlDocumentInput): string {
  return `# ${input.title}\n\n## ${input.databaseName}\n\n\`\`\`sql\n${input.ddlCode}\n\`\`\`\n`;
}
