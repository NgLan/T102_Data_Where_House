/**
 * Tìm khoảng vị trí [startPos, endPos] và số dòng của khối Table trong DBML.
 * @param code Toàn bộ nội dung mã nguồn DBML.
 * @param tableName Tên bảng cần tìm kiếm.
 * @returns Object chứa startPos, endPos và lineIndex nếu tìm thấy; null nếu không tìm thấy.
 */
export function findTableBlockRange(
  code: string,
  tableName: string,
): { startPos: number; endPos: number; lineIndex: number } | null {
  if (!tableName || !code) return null;
  const escapedName = tableName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const tableHeaderRegex = new RegExp(
    `^[ \\t]*Table\\s+(?:[a-zA-Z0-9_"]+\\.)?["']?${escapedName}["']?\\b`,
    "im",
  );
  const match = tableHeaderRegex.exec(code);
  if (!match) return null;

  const startPos = match.index;
  const lineIndex = code.slice(0, startPos).split("\n").length - 1;
  const openBraceIndex = code.indexOf("{", startPos);
  if (openBraceIndex === -1) {
    const nextNewline = code.indexOf("\n", startPos);
    return {
      startPos,
      endPos: nextNewline === -1 ? code.length : nextNewline,
      lineIndex,
    };
  }

  const endPos = findMatchingClosingBrace(code, openBraceIndex);
  return { startPos, endPos, lineIndex };
}

/** Tìm vị trí kết thúc của cặp ngoặc nhọn cân bằng bắt đầu từ openBraceIndex. */
function findMatchingClosingBrace(code: string, openBraceIndex: number): number {
  let depth = 0;
  let inSingleQuote = false;
  let inDoubleQuote = false;
  let inComment = false;

  for (let i = openBraceIndex; i < code.length; i++) {
    const char = code[i];
    const prevChar = i > 0 ? code[i - 1] : "";

    if (!inSingleQuote && !inDoubleQuote && char === "/" && code[i + 1] === "/") {
      inComment = true;
    }
    if (inComment && char === "\n") {
      inComment = false;
      continue;
    }
    if (inComment) continue;

    if (char === "'" && prevChar !== "\\" && !inDoubleQuote) {
      inSingleQuote = !inSingleQuote;
      continue;
    }
    if (char === '"' && prevChar !== "\\" && !inSingleQuote) {
      inDoubleQuote = !inDoubleQuote;
      continue;
    }
    if (inSingleQuote || inDoubleQuote) continue;

    if (char === "{") depth++;
    else if (char === "}") {
      depth--;
      if (depth === 0) return i + 1;
    }
  }

  const nextMatch = /^[ \t]*Table\s+/im.exec(code.slice(openBraceIndex + 1));
  return nextMatch ? openBraceIndex + 1 + nextMatch.index : code.length;
}
